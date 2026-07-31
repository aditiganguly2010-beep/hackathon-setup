import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Structured JSON logging formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure structured JSON logging."""
    log_dir = Path(settings.LOG_FILE_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure no PII in logs
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
    
    # File handler with JSON formatting
    file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
    file_handler.setFormatter(JSONFormatter())
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)
