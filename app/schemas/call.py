from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class CallLogRequest(BaseModel):
    happyrobot_run_id: Optional[str] = None
    call_id: Optional[str] = None
    carrier_mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    selected_load_id: Optional[str] = None
    final_offer: Optional[float] = None
    outcome: Optional[Literal[
        "booked",
        "carrier_not_eligible",
        "no_matching_load",
        "price_rejected",
        "carrier_not_interested",
        "transferred",
        "failed",
    ]] = "failed"
    sentiment: Optional[Literal["positive", "neutral", "negative"]] = "neutral"
    transcript_summary: Optional[str] = None
    full_transcript: Optional[str] = None

    @field_validator("carrier_mc_number", mode="before")
    @classmethod
    def normalize_mc_number(cls, v):
        if v is None:
            return None
        v = str(v).strip()
        if not v.upper().startswith("MC-"):
            v = f"MC-{v}"
        return v


class CallLogResponse(BaseModel):
    success: bool
    call_id: str
    message: str