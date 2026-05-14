import logging
import re
import httpx
from app.config import settings
from app.schemas.carrier import CarrierVerifyResponse

logger = logging.getLogger(__name__)


def _mock_verify(mc_number: str) -> CarrierVerifyResponse:
    mc_upper = mc_number.upper()
    dot_number = str(abs(hash(mc_number)) % 9_000_000 + 1_000_000)
    legal_name = f"Carrier {mc_number} LLC"

    if re.match(r"^MC-\d+$", mc_upper):
        return CarrierVerifyResponse(
            mc_number=mc_number,
            dot_number=dot_number,
            legal_name=legal_name,
            eligible=True,
            authority_status="active",
            safety_status="acceptable",
            reason="Carrier is active and eligible to haul.",
        )
    if mc_upper.startswith("INACTIVE-"):
        return CarrierVerifyResponse(
            mc_number=mc_number,
            dot_number=dot_number,
            legal_name=legal_name,
            eligible=False,
            authority_status="inactive",
            safety_status="acceptable",
            reason="Carrier authority is inactive.",
        )
    return CarrierVerifyResponse(
        mc_number=mc_number,
        dot_number=None,
        legal_name=None,
        eligible=False,
        authority_status="not_found",
        safety_status="unknown",
        reason="MC number not found in FMCSA records.",
    )


def _parse_fmcsa_response(mc_number: str, data: dict) -> CarrierVerifyResponse:
    content = data.get("content", [])
    carrier = content[0].get("carrier", {}) if isinstance(content, list) and len(content) > 0 else {}

    allowed_to_operate = str(carrier.get("allowedToOperate", "N")).upper() == "Y"
    status_code = str(carrier.get("statusCode", "")).upper()
    common_authority = str(carrier.get("commonAuthorityStatus", "")).upper()
    dot_number = str(carrier.get("dotNumber", ""))
    legal_name = carrier.get("legalName") or carrier.get("name")
    safety_rating = str(carrier.get("safetyRating", "")).lower()

    if safety_rating in ("satisfactory", "s", "none", ""):
        safety_status = "acceptable"
    elif safety_rating == "conditional":
        safety_status = "conditional"
    elif safety_rating == "unsatisfactory":
        safety_status = "unsatisfactory"
    else:
        safety_status = "unknown"

    # Carrier is eligible only if:
    # 1. allowedToOperate is Y
    # 2. statusCode is A (Active) — not I (Inactive) or O (Out of Service)
    # 3. commonAuthorityStatus is A (Active) — not I (Inactive) or N (Not authorized)
    # 4. safety_status is not unsatisfactory
    truly_active = (
        allowed_to_operate
        and status_code == "A"
        and common_authority == "A"
    )

    authority_status = "active" if truly_active else "inactive"
    eligible = truly_active and safety_status != "unsatisfactory"

    if not eligible:
        if status_code != "A":
            reason = "Carrier USDOT status is inactive or out of service."
        elif common_authority != "A":
            reason = "Carrier does not have active operating authority."
        elif not allowed_to_operate:
            reason = "Carrier is not allowed to operate."
        else:
            reason = "Carrier safety status is unsatisfactory."
    else:
        reason = "Verified via FMCSA live API."

    return CarrierVerifyResponse(
        mc_number=mc_number,
        dot_number=dot_number or None,
        legal_name=legal_name,
        eligible=eligible,
        authority_status=authority_status,
        safety_status=safety_status,
        reason=reason,
    )


async def verify_carrier(mc_number: str) -> CarrierVerifyResponse:
    if settings.FMCSA_MODE != "live":
        return _mock_verify(mc_number)

    mc_digits = re.sub(r"\D", "", mc_number)
    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_digits}?webKey={settings.FMCSA_WEBKEY}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return _parse_fmcsa_response(mc_number, resp.json())
    except Exception as exc:
        logger.warning("FMCSA live call failed (%s), falling back to mock: %s", mc_number, exc)
        return _mock_verify(mc_number)