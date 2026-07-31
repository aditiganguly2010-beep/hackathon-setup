"""
Rate limiting implementation for API endpoints, particularly for LLM calls.
"""
import time
from collections import defaultdict
from typing import Dict, Optional
from fastapi import Request, HTTPException
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm."""
    
    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier for the client (IP, API key, etc.)
            
        Returns:
            True if allowed, False otherwise
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if timestamp > minute_ago
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.requests_per_minute:
            self.requests[identifier].append(now)
            return True
        
        logger.warning(f"Rate limit exceeded for {identifier}")
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get remaining requests for a client.
        
        Args:
            identifier: Unique identifier for the client
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if timestamp > minute_ago
        ]
        
        return max(0, self.requests_per_minute - len(self.requests[identifier]))


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_ip):
            remaining = self.rate_limiter.get_remaining_requests(client_ip)
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again later. Remaining: {remaining}",
                headers={
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_per_minute),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(int(time.time() + 60))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.rate_limiter.get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response


# Global rate limiter instance
rate_limiter = RateLimiter()
