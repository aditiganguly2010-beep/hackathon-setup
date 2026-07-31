"""
API endpoints for anomalies.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Anomaly
from app.schemas import AnomalyResponse
from app.ai.anomaly_detector import AnomalyDetector
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()
anomaly_detector = AnomalyDetector()


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Retrieve detected anomalies with optional filters.
    """
    query = db.query(Anomaly)
    
    if source_system:
        query = query.filter(Anomaly.source_system == source_system)
    
    if severity:
        query = query.filter(Anomaly.severity == severity)
    
    if start_time:
        query = query.filter(Anomaly.detected_at >= start_time)
    
    if end_time:
        query = query.filter(Anomaly.detected_at <= end_time)
    
    if acknowledged is not None:
        query = query.filter(Anomaly.acknowledged == (1 if acknowledged else 0))
    
    query = query.order_by(Anomaly.detected_at.desc())
    query = query.limit(limit).offset(offset)
    
    anomalies = query.all()
    
    logger.info(f"Retrieved {len(anomalies)} anomalies", extra_data={
        "source_system": source_system,
        "severity": severity
    })
    
    return anomalies


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific anomaly by ID.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Anomaly with ID {anomaly_id} not found")
    
    return anomaly


@router.post("/anomalies/detect")
async def detect_anomalies(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Trigger anomaly detection for a specific source system.
    """
    from app.models import PerformanceMetric, SystemLog
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Get data for analysis
    metrics = db.query(PerformanceMetric).filter(
        PerformanceMetric.source_system == source_system,
        PerformanceMetric.timestamp >= cutoff_time
    ).all()
    
    logs = db.query(SystemLog).filter(
        SystemLog.source_system == source_system,
        SystemLog.timestamp >= cutoff_time
    ).all()
    
    # Detect anomalies
    metric_anomalies = anomaly_detector.detect_metric_anomalies(
        metrics, source_system, db
    )
    
    log_anomalies = anomaly_detector.detect_log_anomalies(
        logs, source_system, db
    )
    
    all_anomalies = metric_anomalies + log_anomalies
    
    # Save anomalies to database
    if all_anomalies:
        db.bulk_save_objects(all_anomalies)
        db.commit()
    
    logger.info(f"Detected {len(all_anomalies)} anomalies for {source_system}")
    
    return {
        "source_system": source_system,
        "period_hours": hours,
        "anomalies_detected": len(all_anomalies),
        "metric_anomalies": len(metric_anomalies),
        "log_anomalies": len(log_anomalies)
    }


@router.put("/anomalies/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an anomaly.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Anomaly with ID {anomaly_id} not found")
    
    anomaly.acknowledged = 1
    db.commit()
    
    logger.info(f"Acknowledged anomaly {anomaly_id}")
    
    return {"message": "Anomaly acknowledged successfully"}


@router.put("/anomalies/{anomaly_id}/false-positive")
async def mark_false_positive(
    anomaly_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark an anomaly as a false positive.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Anomaly with ID {anomaly_id} not found")
    
    anomaly.is_false_positive = 1
    db.commit()
    
    logger.info(f"Marked anomaly {anomaly_id} as false positive")
    
    return {"message": "Anomaly marked as false positive"}
