"""
API endpoints for health scores.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import HealthScore
from app.schemas import HealthScoreResponse
from app.ai.anomaly_detector import AnomalyDetector
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()
anomaly_detector = AnomalyDetector()


@router.get("/health-scores", response_model=List[HealthScoreResponse])
async def get_health_scores(
    source_system: Optional[str] = Query(None, description="Filter by source system"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Retrieve health scores for all systems or a specific system.
    """
    query = db.query(HealthScore)
    
    if source_system:
        query = query.filter(HealthScore.source_system == source_system)
    
    query = query.order_by(HealthScore.calculated_at.desc())
    query = query.limit(limit).offset(offset)
    
    scores = query.all()
    
    logger.info(f"Retrieved {len(scores)} health scores")
    
    return scores


@router.get("/health-scores/{source_system}", response_model=HealthScoreResponse)
async def get_health_score(source_system: str, db: Session = Depends(get_db)):
    """
    Retrieve the latest health score for a specific source system.
    """
    score = db.query(HealthScore).filter(
        HealthScore.source_system == source_system
    ).order_by(HealthScore.calculated_at.desc()).first()
    
    if not score:
        from app.core.exceptions import NotFoundException
        raise NotFoundException(f"Health score for {source_system} not found")
    
    return score


@router.post("/health-scores/calculate")
async def calculate_health_score(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Calculate and update health score for a specific source system.
    """
    # Calculate health score
    score_data = anomaly_detector.calculate_health_score(source_system, db, hours)
    
    if not score_data:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(f"Could not calculate health score for {source_system}")
    
    # Check if health score exists
    existing_score = db.query(HealthScore).filter(
        HealthScore.source_system == source_system
    ).first()
    
    if existing_score:
        # Update existing
        for key, value in score_data.items():
            if hasattr(existing_score, key):
                setattr(existing_score, key, value)
        existing_score.updated_at = datetime.utcnow()
    else:
        # Create new
        new_score = HealthScore(**score_data)
        db.add(new_score)
    
    db.commit()
    
    logger.info(f"Calculated health score for {source_system}", extra_data={
        "overall_score": score_data["overall_score"]
    })
    
    return score_data
