from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class NegotiationEvent(Base):
    __tablename__ = "negotiation_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String, nullable=False)
    load_id = Column(String, nullable=False)
    carrier_mc_number = Column(String, nullable=False)
    round_number = Column(Integer, nullable=False)
    carrier_offer = Column(Float, nullable=False)
    counter_offer = Column(Float, nullable=True)
    decision = Column(String, nullable=False)
    max_authorized_price = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
