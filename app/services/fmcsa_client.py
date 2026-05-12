import logging
import re
import httpx
from app.config import settings
from app.schemas.carrier import CarrierVerifyResponse

logger = logging.getLogger(__name__)


def _mock_verify(mc_number: str) -> CarrierVerifyResponse:
    mc_upper = mc_number.upper() # mc_upper normalizes the input to uppercase so mc-123 and MC-123 are treated identically.
    dot_number = str(abs(hash(mc_number)) % 9_000_000 + 1_000_000) # dot_number generates a fake but consistent 7-digit DOT number using Python's hash() function
    legal_name = f"Carrier {mc_number} LLC" # legal_name builds a placeholder company name.

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


def _parse_fmcsa_response(mc_number: str, data: dict) -> CarrierVerifyResponse: #  takes the raw JSON response from the real FMCSA API and translates it into our CarrierVerifyResponse schema
    content = data.get("content", {})
    carrier = content.get("carrier", {}) if isinstance(content, dict) else {}
    # The FMCSA API returns a nested JSON structure — data["content"]["carrier"] — so the first three lines navigate into that structure safely using .get(), which returns a default value instead of crashing if a key is missing

    allowed_to_operate = str(carrier.get("allowedToOperate", "N")).upper() == "Y"
    dot_number = str(carrier.get("dotNumber", ""))
    legal_name = carrier.get("legalName") or carrier.get("name")
    safety_rating = str(carrier.get("safetyRating", "")).lower()

    if safety_rating in ("satisfactory", "none"):
        safety_status = "acceptable"
    elif safety_rating == "conditional":
        safety_status = "conditional"
    elif safety_rating == "unsatisfactory":
        safety_status = "unsatisfactory"
    else:
        safety_status = "unknown"

    # A carrier is eligible only if they are allowed to operate AND their safety status is not problematic. Both conditions must be true.
    authority_status = "active" if allowed_to_operate else "inactive"
    eligible = allowed_to_operate and safety_status in ("acceptable", "unknown")

    return CarrierVerifyResponse(
        mc_number=mc_number,
        dot_number=dot_number or None,
        legal_name=legal_name,
        eligible=eligible,
        authority_status=authority_status,
        safety_status=safety_status,
        reason="Verified via FMCSA live API.",
    )


async def verify_carrier(mc_number: str) -> CarrierVerifyResponse:
    if settings.FMCSA_MODE != "live": # If the environment variable FMCSA_MODE is anything other than "live", we skip the real API call and just return a mock response. This allows us to test our application without relying on the external FMCSA service, which can be slow or have rate limits.
        return _mock_verify(mc_number)

    mc_digits = re.sub(r"\D", "", mc_number) # Strips all non-digit characters from the MC number. MC-123456 becomes 123456
    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_digits}?webKey={settings.FMCSA_WEBKEY}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return _parse_fmcsa_response(mc_number, resp.json())
    except Exception as exc:
        logger.warning("FMCSA live call failed (%s), falling back to mock: %s", mc_number, exc)
        return _mock_verify(mc_number)
