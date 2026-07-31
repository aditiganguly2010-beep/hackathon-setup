from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AnomalyBase(BaseModel):
    source_system: str = Field(..., description="Source system identifier")
    anomaly_type: str = Field(..., description="Type of anomaly")
    severity: str = Field(..., description="Severity level (Critical, High, Medium, Low)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    description: str = Field(..., description="Anomaly description")
    detected_at: datetime = Field(..., description="Detection timestamp")
    related_metrics: Optional[str] = None
    related_logs: Optional[str] = None


class AnomalyCreate(AnomalyBase):
    pass


class AnomalyResponse(AnomalyBase):
    id: int
    is_false_positive: bool
    acknowledged: bool
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True
