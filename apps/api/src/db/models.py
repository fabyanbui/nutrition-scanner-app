from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True) # UUID
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # Allows future expansion for user accounts

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # Optional link to user
    status = Column(String, default="queue") # queue, running, completed, failed
    progress = Column(Float, default=0.0)
    
    image_id = Column(String, nullable=True) # ID in storage
    image_metadata = Column(JSON, nullable=True) # resolution, size, format
    
    result_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    
    agent_metadata = Column(JSON, nullable=True) # Tracks which agents ran, latency, version
    inference_metadata = Column(JSON, nullable=True) # Tracks model version, temp, prompt tokens
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class FoodAnalysis(Base):
    __tablename__ = "food_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    image_url = Column(String, nullable=True)
    result_json = Column(JSON, nullable=False)
    
    model_version = Column(String, default="unknown")
    processing_time = Column(Float, nullable=False)  # in milliseconds
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
