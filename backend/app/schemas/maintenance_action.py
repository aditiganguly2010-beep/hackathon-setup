from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MaintenanceActionBase(BaseModel):
    source_system: str = Field(..., description="Source system identifier")
    action_type: str = Field(..., description="Action type")
    priority: int = Field(..., ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    estimated_effort: Optional[str] = None
    related_anomaly_id: Optional[int] = None
    status: str = Field(default="Pending", description="Action status")
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class MaintenanceActionCreate(MaintenanceActionBase):
    pass


class MaintenanceActionResponse(MaintenanceActionBase):
    id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True
