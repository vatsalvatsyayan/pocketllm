"""Request queue management service."""
import json
from typing import Optional, Dict, Any
import structlog

from app.config import settings
from app.services.cache_manager import get_redis_client
from app.models import InferenceRequest

logger = structlog.get_logger()


class RequestQueue:
    """Manages FIFO request queue using Redis."""
    
    QUEUE_KEY = "queue:requests"
    
    def __init__(self):
        """Initialize request queue."""
        pass
    
    async def enqueue(self, request: InferenceRequest) -> bool:
        """
        Add request to the queue.
        
        Args:
            request: Inference request to enqueue
            
        Returns:
            True if enqueued, False if queue is full
            
        Raises:
            HTTPException: If queue is full
        """
        redis_client = await get_redis_client()
        
        # Check if using placeholder Redis
        from app.services.cache_manager import PlaceholderRedis
        if isinstance(redis_client, PlaceholderRedis):
            logger.warning("Redis unavailable, queue operations disabled", session_id=request.session_id)
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Queue service unavailable (Redis not connected)",
            )
        
        # Check queue length
        queue_length = await self.get_length()
        
        if queue_length >= settings.MAX_QUEUE_SIZE:
            logger.warning(
                "Queue full",
                queue_length=queue_length,
                max_size=settings.MAX_QUEUE_SIZE,
            )
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Queue is full (max {settings.MAX_QUEUE_SIZE} requests)",
            )
        
        # Add request to queue (LPUSH for FIFO - we'll use RPOP to dequeue)
        request_data = request.model_dump_json()
        await redis_client.lpush(self.QUEUE_KEY, request_data)
        
        logger.debug(
            "Request enqueued",
            session_id=request.session_id,
            queue_length=queue_length + 1,
        )
        return True
    
    async def dequeue(self) -> Optional[InferenceRequest]:
        """
        Remove and return the next request from the queue (FIFO).
        
        Returns:
            InferenceRequest if available, None if queue is empty
        """
        redis_client = await get_redis_client()
        
        # Use RPOP for FIFO (last in, first out when using LPUSH)
        # Actually, for true FIFO with LPUSH, we need RPOP
        request_data = await redis_client.rpop(self.QUEUE_KEY)
        
        if request_data:
            try:
                request = InferenceRequest.model_validate_json(request_data)
                logger.debug("Request dequeued", session_id=request.session_id)
                return request
            except Exception as e:
                logger.error("Failed to parse dequeued request", error=str(e))
                return None
        
        return None
    
    async def get_length(self) -> int:
        """
        Get current queue length.
        
        Returns:
            Number of requests in queue
        """
        redis_client = await get_redis_client()
        from app.services.cache_manager import PlaceholderRedis
        if isinstance(redis_client, PlaceholderRedis):
            return 0
        length = await redis_client.llen(self.QUEUE_KEY)
        return length
    
    async def remove(self, request_id: str) -> bool:
        """
        Remove a specific request from the queue.
        
        Args:
            request_id: Request identifier (using session_id as identifier)
            
        Returns:
            True if removed, False if not found
        """
        redis_client = await get_redis_client()
        
        # Get all items in queue
        items = await redis_client.lrange(self.QUEUE_KEY, 0, -1)
        
        # Find and remove matching request
        removed = False
        for item in items:
            try:
                request_data = json.loads(item)
                if request_data.get("session_id") == request_id:
                    await redis_client.lrem(self.QUEUE_KEY, 1, item)
                    removed = True
                    logger.debug("Request removed from queue", request_id=request_id)
                    break
            except Exception as e:
                logger.warning("Failed to parse queue item", error=str(e))
                continue
        
        return removed
    
    async def clear(self):
        """Clear all requests from the queue."""
        redis_client = await get_redis_client()
        await redis_client.delete(self.QUEUE_KEY)
        logger.info("Queue cleared")

