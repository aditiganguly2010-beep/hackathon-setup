from sqlalchemy import Column, String, Text, DateTime, Integer, Float
from app.models.base import BaseModel


class SystemLog(BaseModel):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_system = Column(String(255), nullable=False, index=True)
    log_level = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_data = Column(Text)  # Original raw log data
    normalized_data = Column(Text)  # JSON string of normalized data
    metadata = Column(Text)  # Additional metadata as JSON
