"""
API endpoints for maintenance actions.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import MaintenanceAction
from app.schemas import MaintenanceActionResponse, MaintenanceActionCreate
from app.ai.summarizer import GenAISummarizer
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()
summarizer = GenAISummarizer()


@router.get("/maintenance-actions", response_model=list[MaintenanceActionResponse])
async def get_maintenance_actions(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Retrieve maintenance actions with optional filters.
    """
    query = db.query(MaintenanceAction)
    
    if source_system:
        query = query.filter(MaintenanceAction.source_system == source_system)
    
    if status:
        query = query.filter(MaintenanceAction.status == status)
    
    if priority:
        query = query.filter(MaintenanceAction.priority == priority)
    
    query = query.order_by(MaintenanceAction.priority.asc(), MaintenanceAction.due_date.asc())
    query = query.limit(limit).offset(offset)
    
    actions = query.all()
    
    logger.info(f"Retrieved {len(actions)} maintenance actions")
    
    return actions


@router.get("/maintenance-actions/{action_id}", response_model=MaintenanceActionResponse)
async def get_maintenance_action(action_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific maintenance action by ID.
    """
    action = db.query(MaintenanceAction).filter(MaintenanceAction.id == action_id).first()
    
    if not action:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Maintenance action with ID {action_id} not found")
    
    return action


@router.post("/maintenance-actions/generate")
async def generate_maintenance_actions(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered maintenance actions for a specific source system.
    """
    # Generate actions using AI
    actions_data = summarizer.generate_maintenance_actions(source_system, db, hours)
    
    # Create maintenance action objects
    actions = []
    for action_data in actions_data:
        action = MaintenanceAction(
            source_system=source_system,
            action_type=action_data.get("action_type", "Investigate"),
            priority=action_data.get("priority", 3),
            title=action_data.get("title", "Untitled Action"),
            description=action_data.get("description", ""),
            estimated_effort=action_data.get("estimated_effort"),
            status="Pending"
        )
        actions.append(action)
    
    # Save to database
    if actions:
        db.bulk_save_objects(actions)
        db.commit()
    
    logger.info(f"Generated {len(actions)} maintenance actions for {source_system}")
    
    return {
        "source_system": source_system,
        "period_hours": hours,
        "actions_generated": len(actions),
        "actions": [action_data for action_data in actions_data]
    }


@router.put("/maintenance-actions/{action_id}/status")
async def update_action_status(
    action_id: int,
    status: str = Query(..., description="New status"),
    db: Session = Depends(get_db)
):
    """
    Update the status of a maintenance action.
    """
    action = db.query(MaintenanceAction).filter(MaintenanceAction.id == action_id).first()
    
    if not action:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Maintenance action with ID {action_id} not found")
    
    valid_statuses = ["Pending", "In Progress", "Scheduled", "Completed"]
    if status not in valid_statuses:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(f"Invalid status. Must be one of: {valid_statuses}")
    
    action.status = status
    
    if status == "Completed":
        action.completed_at = datetime.utcnow()
    
    db.commit()
    
    logger.info(f"Updated maintenance action {action_id} status to {status}")
    
    return {"message": "Status updated successfully"}
