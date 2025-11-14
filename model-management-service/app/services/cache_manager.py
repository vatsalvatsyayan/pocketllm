"""Redis connection and cache management."""
import redis.asyncio as redis
from typing import Optional, Union
import structlog

from app.config import settings

logger = structlog.get_logger()

# Global Redis connection pool
_redis_pool: Optional[redis.ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None
_redis_available: bool = True


class PlaceholderRedis:
    """Placeholder Redis client for when Redis is unavailable."""
    
    async def get(self, key: str) -> None:
        return None
    
    async def setex(self, key: str, time: int, value: str) -> None:
        pass
    
    async def lpush(self, key: str, value: str) -> None:
        pass
    
    async def rpop(self, key: str) -> None:
        return None
    
    async def llen(self, key: str) -> int:
        return 0
    
    async def lrem(self, key: str, count: int, value: str) -> int:
        return 0
    
    async def delete(self, key: str) -> int:
        return 0
    
    async def ping(self) -> bool:
        return False
    
    async def incr(self, key: str) -> int:
        return 0
    
    async def expire(self, key: str, time: int) -> bool:
        return False
    
    async def scan_iter(self, match: str = None):
        return iter([])
    
    async def close(self) -> None:
        pass


async def get_redis_client() -> Union[redis.Redis, PlaceholderRedis]:
    """Get or create Redis client with connection pooling and graceful fallback."""
    global _redis_pool, _redis_client, _redis_available
    
    if not _redis_available:
        return PlaceholderRedis()
    
    if _redis_client is None:
        try:
            _redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _redis_client = redis.Redis(connection_pool=_redis_pool)
            # Test connection
            await _redis_client.ping()
            logger.info("Redis connection pool created", url=settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis unavailable, using placeholder mode", error=str(e))
            _redis_available = False
            _redis_client = None
            return PlaceholderRedis()
    
    return _redis_client


async def close_redis_connection():
    """Close Redis connection pool."""
    global _redis_client, _redis_pool, _redis_available
    
    if _redis_client:
        try:
            await _redis_client.close()
        except Exception:
            pass
        _redis_client = None
    
    if _redis_pool:
        try:
            await _redis_pool.disconnect()
        except Exception:
            pass
        _redis_pool = None
    
    _redis_available = True

