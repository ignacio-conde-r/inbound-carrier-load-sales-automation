from pydantic import BaseModel
from typing import Optional


class MetricsSummary(BaseModel):
    total_calls: int
    booked: int
    booking_rate: float
    ineligible: int
    no_match: int
    price_rejected: int
    avg_agreed_price: Optional[float]
    avg_negotiation_rounds: Optional[float]
    positive_sentiment: int
    negative_sentiment: int
