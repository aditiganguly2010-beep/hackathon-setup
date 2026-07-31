from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class HealthScoreBase(BaseModel):
    source_system: str = Field(..., description="Source system identifier")
    overall_score: int = Field(..., ge=0, le=100, description="Overall health score")
    cpu_score: Optional[int] = Field(None, ge=0, le=100)
    memory_score: Optional[int] = Field(None, ge=0, le=100)
    disk_score: Optional[int] = Field(None, ge=0, le=100)
    network_score: Optional[int] = Field(None, ge=0, le=100)
    log_anomaly_score: Optional[int] = Field(None, ge=0, le=100)
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    trend: Optional[str] = Field(None, description="Health trend")


class HealthScoreCreate(HealthScoreBase):
    pass


class HealthScoreResponse(HealthScoreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True
