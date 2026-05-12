from sqlalchemy import Column, String, Float, Integer, DateTime
from app.models.base import Base


class Load(Base):
    __tablename__ = "loads"

    load_id = Column(String, primary_key=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False) 
    pickup_datetime = Column(DateTime, nullable=False)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False)
    loadboard_rate = Column(Float, nullable=False)
    weight = Column(Integer, nullable=False)
    commodity_type = Column(String, nullable=False)
    miles = Column(Integer, nullable=False)
    notes = Column(String, default="")
    num_of_pieces = Column(Integer, default=0)
    dimensions = Column(String, default="")
    status = Column(String, default="available")
