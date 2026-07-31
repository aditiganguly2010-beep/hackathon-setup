from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class PerformanceMetric(BaseModel):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    source_system = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False, index=True)  # CPU, Memory, Disk, Network
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50))  # %, MB, GB, Mbps
    timestamp = Column(DateTime, nullable=False, index=True)
