from sqlalchemy import Column, String, Text, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Anomaly(BaseModel):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    source_system = Column(String(255), nullable=False, index=True)
    anomaly_type = Column(String(100), nullable=False, index=True)  # Log Spike, High Memory, CPU Saturation
    severity = Column(String(50), nullable=False, index=True)  # Critical, High, Medium, Low
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    description = Column(Text, nullable=False)
    detected_at = Column(DateTime, nullable=False, index=True)
    related_metrics = Column(Text)  # JSON array of related metric IDs
    related_logs = Column(Text)  # JSON array of related log IDs
    is_false_positive = Column(Integer, default=0)  # Boolean as integer
    acknowledged = Column(Integer, default=0)  # Boolean as integer
