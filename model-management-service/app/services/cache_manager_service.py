"""Cache Manager - Orchestrates L1 and L2 caches."""
from typing import Optional, Tuple
import structlog

from app.services.l1_cache import L1CacheHandler
from app.services.l2_cache import L2CacheHandler

logger = structlog.get_logger()


class CacheManager:
    """Orchestrates L1 and L2 cache operations."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.l1_cache = L1CacheHandler()
        self.l2_cache = L2CacheHandler()
    
    async def check_cache(
        self,
        prompt: str,
        model_config: Optional[dict] = None,
        context: Optional[str] = None,
        messages: Optional[list] = None,
    ) -> Optional[Tuple[str, str]]:
        """
        Check both L1 and L2 caches for a match.
        
        Args:
            prompt: User prompt
            model_config: Optional model configuration
            context: Full conversation context (for accurate cache key)
            messages: List of previous messages (if context not available)
            
        Returns:
            Tuple of (response, cache_type) if found, None otherwise
            cache_type is either "l1" or "l2"
        """
        try:
            # Try L1 cache first (exact match) - includes context in hash
            prompt_hash = self.l1_cache.generate_hash(prompt, model_config, context, messages)
            l1_response = await self.l1_cache.check_exact_match(prompt_hash)
            
            if l1_response:
                logger.debug("Cache hit: L1", hash=prompt_hash[:16], has_context=bool(context or messages))
                return (l1_response, "l1")
            
            # Try L2 cache (semantic similarity)
            # Note: L2 cache uses embeddings which don't capture context well
            # For now, we'll still check it but it may return incorrect results
            # TODO: Improve L2 cache to consider context
            embedding = await self.l2_cache.generate_embedding(prompt)
            l2_result = await self.l2_cache.find_similar(embedding)
            
            if l2_result:
                response, similarity = l2_result
                logger.debug("Cache hit: L2", similarity=similarity, hash=prompt_hash[:16])
                # Warn that L2 cache doesn't consider context
                if context or messages:
                    logger.warning("L2 cache hit but context not considered - may be inaccurate")
                return (response, "l2")
            
            logger.debug("Cache miss", hash=prompt_hash[:16], has_context=bool(context or messages))
            return None
        except Exception as e:
            logger.warning("Cache check failed (Redis may be unavailable)", error=str(e))
            return None
    
    async def store_in_cache(
        self,
        prompt: str,
        response: str,
        model_config: Optional[dict] = None,
        context: Optional[str] = None,
        messages: Optional[list] = None,
    ):
        """
        Store response in both L1 and L2 caches.
        
        Args:
            prompt: User prompt
            response: Model response
            model_config: Optional model configuration
            context: Full conversation context (for accurate cache key)
            messages: List of previous messages (if context not available)
        """
        try:
            # Include context in hash for accurate caching
            prompt_hash = self.l1_cache.generate_hash(prompt, model_config, context, messages)
            
            # Store in L1 cache
            await self.l1_cache.store(prompt_hash, response)
            
            # Store in L2 cache (async, don't wait)
            # Note: L2 cache doesn't consider context, so it may cache incorrectly
            # This is a limitation of semantic similarity caching
            try:
                embedding = await self.l2_cache.generate_embedding(prompt)
                await self.l2_cache.store(embedding, response, prompt_hash)
            except Exception as e:
                logger.warning("Failed to store in L2 cache", error=str(e))
            
            logger.debug("Response cached in L1 and L2", hash=prompt_hash[:16], has_context=bool(context or messages))
        except Exception as e:
            logger.warning("Failed to store in cache (Redis may be unavailable)", error=str(e))

