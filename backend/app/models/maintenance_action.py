from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class MaintenanceAction(BaseModel):
    __tablename__ = "maintenance_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    source_system = Column(String(255), nullable=False, index=True)
    action_type = Column(String(100), nullable=False)  # Restart, Cleanup, Update, Investigate
    priority = Column(Integer, nullable=False, index=True)  # 1 (highest) to 5 (lowest)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    estimated_effort = Column(String(100))  # e.g., "30 minutes", "2 hours"
    related_anomaly_id = Column(Integer, ForeignKey("anomalies.id"))
    status = Column(String(50), nullable=False, default="Pending")  # Pending, In Progress, Scheduled, Completed
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)
