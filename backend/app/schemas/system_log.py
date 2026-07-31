from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SystemLogBase(BaseModel):
    source_system: str = Field(..., description="Source system identifier")
    log_level: str = Field(..., description="Log level (INFO, WARNING, ERROR, CRITICAL)")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Log timestamp")
    raw_data: Optional[str] = None
    normalized_data: Optional[str] = None
    metadata: Optional[str] = None


class SystemLogCreate(SystemLogBase):
    pass


class SystemLogResponse(SystemLogBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        from_attributes = True
