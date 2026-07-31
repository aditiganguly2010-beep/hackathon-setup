"""
API endpoints for AI summaries.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.ai.summarizer import GenAISummarizer
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()
summarizer = GenAISummarizer()


@router.get("/summaries/system")
async def get_system_summary(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered natural language summary of system status.
    """
    summary = summarizer.generate_system_summary(source_system, db, hours)
    
    logger.info(f"Generated system summary for {source_system}")
    
    return summary


@router.get("/summaries/stream")
async def get_system_summary_stream(
    source_system: str = Query(..., description="Source system identifier"),
    hours: int = Query(24, ge=1, le=168, description="Number of hours to analyze"),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-powered summary with streaming response (SSE).
    """
    from fastapi.responses import StreamingResponse
    import json
    
    summary = summarizer.generate_system_summary(source_system, db, hours)
    
    async def generate():
        # Stream the summary as JSON
        yield f"data: {json.dumps(summary)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
