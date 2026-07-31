from sqlalchemy import Column, String, Integer, Float, DateTime
from app.models.base import BaseModel


class HealthScore(BaseModel):
    __tablename__ = "health_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    source_system = Column(String(255), nullable=False, unique=True, index=True)
    overall_score = Column(Integer, nullable=False)  # 0 to 100
    cpu_score = Column(Integer)  # 0 to 100
    memory_score = Column(Integer)  # 0 to 100
    disk_score = Column(Integer)  # 0 to 100
    network_score = Column(Integer)  # 0 to 100
    log_anomaly_score = Column(Integer)  # 0 to 100
    calculated_at = Column(DateTime, nullable=False, index=True)
    trend = Column(String(20))  # Improving, Stable, Degrading
