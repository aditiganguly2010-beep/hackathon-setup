"""
API endpoints for system logs.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import SystemLog
from app.schemas import SystemLogResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/logs", response_model=List[SystemLogResponse])
async def get_logs(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    log_level: Optional[str] = Query(None, description="Filter by log level"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Retrieve system logs with optional filters.
    """
    query = db.query(SystemLog)
    
    if source_system:
        query = query.filter(SystemLog.source_system == source_system)
    
    if log_level:
        query = query.filter(SystemLog.log_level == log_level)
    
    if start_time:
        query = query.filter(SystemLog.timestamp >= start_time)
    
    if end_time:
        query = query.filter(SystemLog.timestamp <= end_time)
    
    query = query.order_by(SystemLog.timestamp.desc())
    query = query.limit(limit).offset(offset)
    
    logs = query.all()
    
    logger.info(f"Retrieved {len(logs)} logs", extra_data={
        "source_system": source_system,
        "log_level": log_level
    })
    
    return logs


@router.get("/logs/{log_id}", response_model=SystemLogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific log by ID.
    """
    log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
    
    if not log:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Log with ID {log_id} not found")
    
    return log


@router.get("/logs/recent")
async def get_recent_logs(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Retrieve recent logs for a specific source system.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    logs = db.query(SystemLog).filter(
        SystemLog.source_system == source_system,
        SystemLog.timestamp >= cutoff_time
    ).order_by(SystemLog.timestamp.desc()).limit(limit).all()
    
    logger.info(f"Retrieved {len(logs)} recent logs for {source_system}")
    
    return logs
