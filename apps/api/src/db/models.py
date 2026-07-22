from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class FoodAnalysis(Base):
    __tablename__ = "food_analysis"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=True)
    result_json = Column(JSON, nullable=False)
    model_version = Column(String, default="mock-v1")
    processing_time = Column(Float, nullable=False)  # in milliseconds
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
