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
    ) -> Optional[Tuple[str, str]]:
        """
        Check both L1 and L2 caches for a match.
        
        Args:
            prompt: User prompt
            model_config: Optional model configuration
            
        Returns:
            Tuple of (response, cache_type) if found, None otherwise
            cache_type is either "l1" or "l2"
        """
        try:
            # Try L1 cache first (exact match)
            prompt_hash = self.l1_cache.generate_hash(prompt, model_config)
            l1_response = await self.l1_cache.check_exact_match(prompt_hash)
            
            if l1_response:
                logger.debug("Cache hit: L1", hash=prompt_hash[:16])
                return (l1_response, "l1")
            
            # Try L2 cache (semantic similarity)
            embedding = await self.l2_cache.generate_embedding(prompt)
            l2_result = await self.l2_cache.find_similar(embedding)
            
            if l2_result:
                response, similarity = l2_result
                logger.debug("Cache hit: L2", similarity=similarity, hash=prompt_hash[:16])
                return (response, "l2")
            
            logger.debug("Cache miss", hash=prompt_hash[:16])
            return None
        except Exception as e:
            logger.warning("Cache check failed (Redis may be unavailable)", error=str(e))
            return None
    
    async def store_in_cache(
        self,
        prompt: str,
        response: str,
        model_config: Optional[dict] = None,
    ):
        """
        Store response in both L1 and L2 caches.
        
        Args:
            prompt: User prompt
            response: Model response
            model_config: Optional model configuration
        """
        try:
            prompt_hash = self.l1_cache.generate_hash(prompt, model_config)
            
            # Store in L1 cache
            await self.l1_cache.store(prompt_hash, response)
            
            # Store in L2 cache (async, don't wait)
            try:
                embedding = await self.l2_cache.generate_embedding(prompt)
                await self.l2_cache.store(embedding, response, prompt_hash)
            except Exception as e:
                logger.warning("Failed to store in L2 cache", error=str(e))
            
            logger.debug("Response cached in L1 and L2", hash=prompt_hash[:16])
        except Exception as e:
            logger.warning("Failed to store in cache (Redis may be unavailable)", error=str(e))

