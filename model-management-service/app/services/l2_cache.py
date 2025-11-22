"""L2 Cache Handler - Semantic similarity caching."""
import json
from typing import List, Optional, Dict, Any, Tuple
import structlog

from app.config import settings
from app.services.cache_manager import get_redis_client
from app.utils.embeddings import generate_embedding, cosine_similarity

logger = structlog.get_logger()


class L2CacheHandler:
    """Handles L2 cache (semantic similarity) operations."""
    
    def __init__(self):
        """Initialize L2 cache handler."""
        pass
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        return generate_embedding(text)
    
    async def find_similar(
        self,
        embedding: List[float],
        threshold: float = None,
    ) -> Optional[Tuple[str, float]]:
        """
        Find similar cached response using cosine similarity.
        
        Args:
            embedding: Query embedding vector
            threshold: Similarity threshold (defaults to config value)
            
        Returns:
            Tuple of (cached_response, similarity_score) if found, None otherwise
        """
        threshold = threshold or settings.CACHE_SIMILARITY_THRESHOLD
        redis_client = await get_redis_client()
        
        try:
            # Get all L2 cache keys
            pattern = "cache:l2:*"
            keys = []
            # redis_client.scan_iter returns an async iterator, so we can use async for
            # However, if redis_client is not an async client, this would fail.
            # Assuming redis_client is from aioredis or redis.asyncio
            
            # Fix: Ensure we are using the async iterator correctly
            # The error "'async for' requires an object with __aiter__ method, got coroutine"
            # suggests that scan_iter might be a coroutine itself in some versions or wrappers?
            # Or maybe get_redis_client() returns a wrapper?
            
            # Let's check how scan_iter is called. 
            # In redis-py 5.x (async), scan_iter is an async generator.
            
            # If the error says "got coroutine", it means something we are iterating over IS a coroutine.
            # Maybe redis_client.scan_iter(match=pattern) is NOT a coroutine but returns an async iterator.
            # Wait, if it says "got coroutine", maybe we are doing `async for key in await func()`?
            # No, the code was `async for key in redis_client.scan_iter(match=pattern):`
            
            # If redis_client.scan_iter IS a coroutine (returns a future), then we should await it?
            # But scan_iter usually returns an iterator.
            
            # Let's try to use keys() instead for simplicity if scan_iter is problematic, 
            # though keys() is blocking/heavy. But for L2 cache with limited keys it might be ok for now.
            # Better: Let's look at the error again.
            # "async for' requires an object with __aiter__ method, got coroutine"
            
            # This implies `redis_client.scan_iter(match=pattern)` returned a coroutine object.
            # This happens if `scan_iter` is defined as `async def scan_iter(...)`.
            # If so, we need to await it? `async for key in await redis_client.scan_iter(...)`?
            # But `async for` expects an async iterator.
            
            # Let's try a safer approach using `keys` for now to fix the immediate crash, 
            # as we likely don't have millions of keys yet.
            
            keys = await redis_client.keys(pattern)
            
            best_match = None
            best_similarity = 0.0
            
            # Compare with each cached embedding
            for key in keys:
                try:
                    cached_data = await redis_client.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        cached_embedding = data.get("embedding")
                        cached_response = data.get("response")
                        
                        if cached_embedding and cached_response:
                            similarity = cosine_similarity(embedding, cached_embedding)
                            
                            if similarity > best_similarity and similarity >= threshold:
                                best_similarity = similarity
                                best_match = (cached_response, similarity)
                except Exception as e:
                    logger.warning("Failed to process L2 cache entry", key=key, error=str(e))
                    continue
            
            if best_match:
                logger.debug(
                    "L2 cache hit",
                    similarity=best_similarity,
                    threshold=threshold,
                )
                return best_match
            else:
                logger.debug("L2 cache miss", threshold=threshold)
                return None
                
        except Exception as e:
            logger.error("L2 cache search failed", error=str(e))
            return None
    
    async def store(
        self,
        embedding: List[float],
        response: str,
        prompt_hash: str,
        ttl: int = None,
    ):
        """
        Store response with embedding in L2 cache.
        
        Args:
            embedding: Embedding vector
            response: Model response
            prompt_hash: Hash of the prompt (for key generation)
            ttl: Time to live in seconds (defaults to config value)
        """
        ttl = ttl or settings.L2_CACHE_TTL
        redis_client = await get_redis_client()
        cache_key = f"cache:l2:{prompt_hash}"
        
        try:
            cache_data = {
                "embedding": embedding,
                "response": response,
            }
            cache_json = json.dumps(cache_data)
            await redis_client.setex(cache_key, ttl, cache_json)
            logger.debug("L2 cache stored", hash=prompt_hash[:16], ttl=ttl)
        except Exception as e:
            logger.error("L2 cache store failed", hash=prompt_hash[:16], error=str(e))

