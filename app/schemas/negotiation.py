from pydantic import BaseModel, Field
from typing import Optional, Literal


class NegotiationEvaluateRequest(BaseModel):
    call_id: str
    load_id: str
    carrier_mc_number: str
    round_number: int = Field(..., ge=1, le=3)
    carrier_offer: float = Field(..., gt=0)
    previous_counter_offer: Optional[float] = None


class NegotiationEvaluateResponse(BaseModel):
    decision: Literal["accept", "counter", "reject", "escalate"]
    agreed_price: Optional[float] = None
    counter_offer: Optional[float] = None
    max_authorized_price: float
    round_number: int
    remaining_rounds: int
    reason: str
    agent_message: str
