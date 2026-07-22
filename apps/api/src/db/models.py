from sqlalchemy import Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="queue") # queue, running, completed, failed
    progress = Column(Float, default=0.0)
    result_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class FoodAnalysis(Base):

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=True)
    result_json = Column(JSON, nullable=False)
    model_version = Column(String, default="mock-v1")
    processing_time = Column(Float, nullable=False)  # in milliseconds
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
