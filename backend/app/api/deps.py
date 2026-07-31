"""
Common dependencies for API endpoints.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_db_session() -> Generator:
    """Get database session dependency."""
    yield from get_db()


class SourceSystemChecker:
    """Check if source system exists."""
    
    def __init__(self, source_system: str):
        self.source_system = source_system
    
    def __call__(self, db: Session = Depends(get_db_session)) -> str:
        """Validate source system exists."""
        # For now, just return the source system
        # In production, you might want to validate against a list of known systems
        valid_systems = [
            "legacy-crm",
            "legacy-erp",
            "legacy-inventory",
            "legacy-payroll",
            "legacy-hris"
        ]
        
        if self.source_system not in valid_systems:
            logger.warning(f"Unknown source system: {self.source_system}")
            # Allow anyway for flexibility
        
        return self.source_system
