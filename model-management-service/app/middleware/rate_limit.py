"""Rate limiting middleware."""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import structlog

from app.config import settings
from app.services.cache_manager import get_redis_client

logger = structlog.get_logger()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting per user."""
    
    # Paths that don't require rate limiting
    EXCLUDED_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc", "/api/v1/metrics"}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check rate limits."""
        # Skip rate limiting for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Skip rate limiting for WebSocket connections (handled separately)
        if request.url.path.startswith("/ws"):
            return await call_next(request)
        
        # Use IP address for rate limiting (no auth required)
        user_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        try:
            redis_client = await get_redis_client()
            from app.services.cache_manager import PlaceholderRedis
            
            # If Redis is unavailable, skip rate limiting (fail open)
            if isinstance(redis_client, PlaceholderRedis):
                logger.debug("Redis unavailable, skipping rate limiting", user_id=user_id)
                return await call_next(request)
            
            current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
            rate_limit_key = f"ratelimit:{user_id}:{current_hour}"
            
            # Increment counter
            current_count = await redis_client.incr(rate_limit_key)
            
            # Set TTL if this is the first request in this hour
            if current_count == 1:
                await redis_client.expire(rate_limit_key, 3600)  # 1 hour
            
            # Check if limit exceeded
            if current_count > settings.MAX_REQUESTS_PER_HOUR:
                logger.warning(
                    "Rate limit exceeded",
                    user_id=user_id,
                    count=current_count,
                    limit=settings.MAX_REQUESTS_PER_HOUR,
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {settings.MAX_REQUESTS_PER_HOUR} requests per hour",
                    headers={
                        "X-RateLimit-Limit": str(settings.MAX_REQUESTS_PER_HOUR),
                        "X-RateLimit-Remaining": str(max(0, settings.MAX_REQUESTS_PER_HOUR - current_count)),
                        "Retry-After": "3600",
                    },
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.MAX_REQUESTS_PER_HOUR)
            response.headers["X-RateLimit-Remaining"] = str(max(0, settings.MAX_REQUESTS_PER_HOUR - current_count))
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Rate limit check failed, allowing request", error=str(e))
            # On error, allow request through (fail open)
            return await call_next(request)

