"""
In-memory cache implementation for reducing LLM latency and cost.
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class InMemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl_seconds: int = None):
        self.ttl_seconds = ttl_seconds or settings.CACHE_TTL_SECONDS
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate a cache key from data."""
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, (dict, list)) else str(data)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, prefix: str, data: Any) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            prefix: Key prefix
            data: Data to generate key from
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        key = self._generate_key(prefix, data)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.utcnow() > entry["expires_at"]:
            del self.cache[key]
            logger.debug(f"Cache entry expired: {key}")
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry["value"]
    
    def set(self, prefix: str, data: Any, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set item in cache.
        
        Args:
            prefix: Key prefix
            data: Data to generate key from
            value: Value to cache
            ttl_seconds: Custom TTL in seconds
        """
        key = self._generate_key(prefix, data)
        ttl = ttl_seconds or self.ttl_seconds
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
        
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def invalidate(self, prefix: str, data: Any) -> None:
        """
        Invalidate a specific cache entry.
        
        Args:
            prefix: Key prefix
            data: Data to generate key from
        """
        key = self._generate_key(prefix, data)
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache invalidated: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> None:
        """Remove all expired entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache instance
cache = InMemoryCache()
