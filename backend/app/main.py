"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    AppException,
    NotFoundException,
    BadRequestException,
    ValidationException,
    DatabaseException,
    ExternalServiceException,
    app_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler
)
from app.api import health, logs, metrics, anomalies, health_scores, maintenance, summaries, etl
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting application")
    yield
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="Legacy System Health Monitor API",
    description="AI-driven health monitor for legacy systems",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(logs.router, prefix="/api", tags=["Logs"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(anomalies.router, prefix="/api", tags=["Anomalies"])
app.include_router(health_scores.router, prefix="/api", tags=["Health Scores"])
app.include_router(maintenance.router, prefix="/api", tags=["Maintenance"])
app.include_router(summaries.router, prefix="/api", tags=["Summaries"])
app.include_router(etl.router, prefix="/api", tags=["ETL"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Legacy System Health Monitor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
