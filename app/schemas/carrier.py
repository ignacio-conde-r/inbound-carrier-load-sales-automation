from pydantic import BaseModel, Field
from typing import Optional, Literal


class CarrierVerifyRequest(BaseModel):
    mc_number: str = Field(..., min_length=2)
    caller_phone: Optional[str] = None


class CarrierVerifyResponse(BaseModel):
    mc_number: str
    dot_number: Optional[str] = None
    legal_name: Optional[str] = None
    eligible: bool
    authority_status: Literal["active", "inactive", "not_found", "unknown"]
    safety_status: Literal["acceptable", "conditional", "unsatisfactory", "unknown"]
    reason: str
