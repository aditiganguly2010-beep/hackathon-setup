from sqlalchemy import Column, String, Text, DateTime, Integer
from app.models.base import BaseModel


class IncidentRecord(BaseModel):
    __tablename__ = "incident_records"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(255), unique=True, nullable=False, index=True)
    source_system = Column(String(255), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)  # Critical, High, Medium, Low
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="Open")  # Open, In Progress, Resolved
    detected_at = Column(DateTime, nullable=False, index=True)
    resolved_at = Column(DateTime)
    root_cause = Column(Text)
    resolution_notes = Column(Text)
