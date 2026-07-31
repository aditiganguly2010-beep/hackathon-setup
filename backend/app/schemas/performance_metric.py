from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PerformanceMetricBase(BaseModel):
    source_system: str = Field(..., description="Source system identifier")
    metric_type: str = Field(..., description="Metric type (CPU, Memory, Disk, Network)")
    metric_value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    timestamp: datetime = Field(..., description="Metric timestamp")


class PerformanceMetricCreate(PerformanceMetricBase):
    pass


class PerformanceMetricResponse(PerformanceMetricBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True
