"""
API endpoints for performance metrics.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import PerformanceMetric
from app.schemas import PerformanceMetricResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/metrics", response_model=List[PerformanceMetricResponse])
async def get_metrics(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    start_time: Optional[datetime] = Query(None, description="Start time filter"),
    end_time: Optional[datetime] = Query(None, description="End time filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Retrieve performance metrics with optional filters.
    """
    query = db.query(PerformanceMetric)
    
    if source_system:
        query = query.filter(PerformanceMetric.source_system == source_system)
    
    if metric_type:
        query = query.filter(PerformanceMetric.metric_type == metric_type)
    
    if start_time:
        query = query.filter(PerformanceMetric.timestamp >= start_time)
    
    if end_time:
        query = query.filter(PerformanceMetric.timestamp <= end_time)
    
    query = query.order_by(PerformanceMetric.timestamp.desc())
    query = query.limit(limit).offset(offset)
    
    metrics = query.all()
    
    logger.info(f"Retrieved {len(metrics)} metrics", extra_data={
        "source_system": source_system,
        "metric_type": metric_type
    })
    
    return metrics


@router.get("/metrics/{metric_id}", response_model=PerformanceMetricResponse)
async def get_metric(metric_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific metric by ID.
    """
    metric = db.query(PerformanceMetric).filter(PerformanceMetric.id == metric_id).first()
    
    if not metric:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Metric with ID {metric_id} not found")
    
    return metric


@router.get("/metrics/aggregate")
async def get_aggregated_metrics(
    source_system: str = Query(..., description="Source system identifier"),
    metric_type: str = Query(..., description="Metric type"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to aggregate"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics (avg, min, max) for a time period.
    """
    from sqlalchemy import func
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = db.query(
        func.avg(PerformanceMetric.metric_value).label('avg'),
        func.min(PerformanceMetric.metric_value).label('min'),
        func.max(PerformanceMetric.metric_value).label('max'),
        func.count(PerformanceMetric.id).label('count')
    ).filter(
        PerformanceMetric.source_system == source_system,
        PerformanceMetric.metric_type == metric_type,
        PerformanceMetric.timestamp >= cutoff_time
    ).first()
    
    return {
        "source_system": source_system,
        "metric_type": metric_type,
        "period_hours": hours,
        "average": float(result.avg) if result.avg else None,
        "minimum": float(result.min) if result.min is not None else None,
        "maximum": float(result.max) if result.max is not None else None,
        "count": result.count
    }
