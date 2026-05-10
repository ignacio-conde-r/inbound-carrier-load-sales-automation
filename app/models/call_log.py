from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.sql import func
from app.models.base import Base


class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(String, unique=True, nullable=False)
    happyrobot_run_id = Column(String, nullable=True)
    carrier_mc_number = Column(String, nullable=True)
    carrier_name = Column(String, nullable=True)
    selected_load_id = Column(String, nullable=True)
    final_offer = Column(Float, nullable=True)
    outcome = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)
    transcript_summary = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
