"""
API endpoints for ETL operations.
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.etl.pipeline import ETLPipeline
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()
etl_pipeline = ETLPipeline()


@router.post("/etl/ingest/logs")
async def ingest_logs(
    source_system: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingest log data from a file.
    """
    content = await file.read()
    raw_logs = content.decode('utf-8').splitlines()
    
    # Filter empty lines
    raw_logs = [log.strip() for log in raw_logs if log.strip()]
    
    def process_logs():
        count = etl_pipeline.ingest_logs(raw_logs, source_system, db)
        logger.info(f"Background log ingestion completed: {count} logs")
    
    background_tasks.add_task(process_logs)
    
    return {
        "message": "Log ingestion started",
        "source_system": source_system,
        "file_name": file.filename,
        "log_count": len(raw_logs)
    }


@router.post("/etl/ingest/metrics")
async def ingest_metrics(
    source_system: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingest metric data from a file.
    """
    content = await file.read()
    raw_metrics = content.decode('utf-8').splitlines()
    
    # Filter empty lines
    raw_metrics = [metric.strip() for metric in raw_metrics if metric.strip()]
    
    def process_metrics():
        count = etl_pipeline.ingest_metrics(raw_metrics, source_system, db)
        logger.info(f"Background metric ingestion completed: {count} metrics")
    
    background_tasks.add_task(process_metrics)
    
    return {
        "message": "Metric ingestion started",
        "source_system": source_system,
        "file_name": file.filename,
        "metric_count": len(raw_metrics)
    }


@router.post("/etl/ingest/logs/batch")
async def ingest_logs_batch(
    source_system: str,
    raw_logs: List[str],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingest log data from a batch of strings.
    """
    def process_logs():
        count = etl_pipeline.ingest_logs(raw_logs, source_system, db)
        logger.info(f"Background log ingestion completed: {count} logs")
    
    background_tasks.add_task(process_logs)
    
    return {
        "message": "Log ingestion started",
        "source_system": source_system,
        "log_count": len(raw_logs)
    }


@router.post("/etl/ingest/metrics/batch")
async def ingest_metrics_batch(
    source_system: str,
    raw_metrics: List[str],
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Ingest metric data from a batch of strings.
    """
    def process_metrics():
        count = etl_pipeline.ingest_metrics(raw_metrics, source_system, db)
        logger.info(f"Background metric ingestion completed: {count} metrics")
    
    background_tasks.add_task(process_metrics)
    
    return {
        "message": "Metric ingestion started",
        "source_system": source_system,
        "metric_count": len(raw_metrics)
    }
