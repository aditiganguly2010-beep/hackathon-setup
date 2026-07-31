"""
Global exception handling for the API.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found exception."""
    
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message, status_code=404, details=details)


class BadRequestException(AppException):
    """Bad request exception."""
    
    def __init__(self, message: str = "Bad request", details: dict = None):
        super().__init__(message, status_code=400, details=details)


class ValidationException(AppException):
    """Validation exception."""
    
    def __init__(self, message: str = "Validation error", details: dict = None):
        super().__init__(message, status_code=422, details=details)


class DatabaseException(AppException):
    """Database exception."""
    
    def __init__(self, message: str = "Database error", details: dict = None):
        super().__init__(message, status_code=500, details=details)


class ExternalServiceException(AppException):
    """External service exception (e.g., LLM API)."""
    
    def __init__(self, message: str = "External service error", details: dict = None):
        super().__init__(message, status_code=503, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions."""
    logger.error(
        "Application exception",
        extra_data={
            "exception_type": type(exc).__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": type(exc).__name__,
                "details": exc.details
            }
        }
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation exceptions."""
    logger.warning(
        "Validation error",
        extra_data={
            "errors": exc.errors(),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "type": "ValidationError",
                "details": exc.errors()
            }
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database exceptions."""
    logger.error(
        "Database error",
        extra_data={
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Database error occurred",
                "type": "DatabaseError",
                "details": {}
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(
        "Unhandled exception",
        extra_data={
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "type": "InternalServerError",
                "details": {}
            }
        }
    )
