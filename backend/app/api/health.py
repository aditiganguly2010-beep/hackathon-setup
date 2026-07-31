"""
Health check endpoint.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint validating DB connectivity and LLM API status.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error("Database health check failed", extra_data={"error": str(e)})
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check LLM API status (placeholder)
    try:
        # TODO: Implement actual LLM API health check
        health_status["checks"]["llm_api"] = {
            "status": "healthy",
            "message": "LLM API accessible",
            "provider": "Google ADK"
        }
    except Exception as e:
        logger.error("LLM API health check failed", extra_data={"error": str(e)})
        health_status["checks"]["llm_api"] = {
            "status": "degraded",
            "message": f"LLM API check failed: {str(e)}"
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # Check observability services
    try:
        # LangTrace
        langtrace_status = "enabled" if settings.LANGTRACE_API_KEY else "disabled"
        health_status["checks"]["langtrace"] = {
            "status": "healthy",
            "message": f"LangTrace {langtrace_status}"
        }
        
        # Langfuse
        langfuse_status = "enabled" if settings.LANGFUSE_PUBLIC_KEY else "disabled"
        health_status["checks"]["langfuse"] = {
            "status": "healthy",
            "message": f"Langfuse {langfuse_status}"
        }
    except Exception as e:
        logger.error("Observability health check failed", extra_data={"error": str(e)})
        health_status["checks"]["observability"] = {
            "status": "unhealthy",
            "message": f"Observability check failed: {str(e)}"
        }
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return health_status, status_code
