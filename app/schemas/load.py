from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class LoadSearchRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[Literal["Dry Van", "Reefer", "Flatbed"]] = None
    pickup_after: Optional[datetime] = None
    pickup_before: Optional[datetime] = None
    max_weight: Optional[int] = Field(default=None, gt=0)


class LoadOption(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    weight: int
    commodity_type: str
    miles: int
    notes: Optional[str] = None
    match_score: float
    pitch_summary: str


class LoadSearchResponse(BaseModel):
    matches_found: bool
    total_matches: int
    recommended_load: Optional[LoadOption] = None
    alternatives: list[LoadOption] = []
