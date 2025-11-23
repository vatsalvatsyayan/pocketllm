"""L1 Cache Handler - Exact match caching."""
import hashlib
import json
from typing import Optional, Dict, Any
import structlog

from app.config import settings
from app.services.cache_manager import get_redis_client

logger = structlog.get_logger()


class L1CacheHandler:
    """Handles L1 cache (exact match) operations."""
    
    def __init__(self):
        """Initialize L1 cache handler."""
        pass
    
    def generate_hash(
        self, 
        prompt: str, 
        model_config: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None,
        messages: Optional[list] = None,
    ) -> str:
        """
        Generate SHA256 hash for prompt, context, and model config.
        
        Args:
            prompt: User prompt
            model_config: Optional model configuration
            context: Full conversation context (if available)
            messages: List of previous messages (if context not available)
            
        Returns:
            SHA256 hash string
        """
        # Build context string if not provided
        if context is None and messages:
            # Create a context signature from messages - use full content for accurate cache keys
            # This ensures same prompt in different conversation contexts gets different cache keys
            # IMPORTANT: Use the same format as build_context to ensure consistency
            context_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Skip system messages in history (they're handled separately)
                if role == "system":
                    continue
                # Use full content (not truncated) for accurate cache key generation
                # Format matches build_context: "User: content" or "Assistant: content"
                if role == "user":
                    context_parts.append(f"User: {content}")
                elif role == "assistant":
                    context_parts.append(f"Assistant: {content}")
            context = "\n".join(context_parts)  # Use newline separator to match build_context format
        
        # Create hash input - include FULL context to ensure same prompt in different contexts gets different cache key
        # The context includes all previous messages, ensuring accurate cache hits
        # Normalize context: if empty string, use empty; otherwise use as-is
        context_str = context if context else ""
        
        hash_input = {
            "prompt": prompt,
            "context": context_str,  # Include FULL context in hash for accurate caching
            "model_config": model_config or {},
        }
        
        # Convert to JSON string and hash
        hash_string = json.dumps(hash_input, sort_keys=True)
        hash_obj = hashlib.sha256(hash_string.encode('utf-8'))
        return hash_obj.hexdigest()
    
    async def check_exact_match(self, hash: str) -> Optional[str]:
        """
        Check if exact match exists in cache.
        
        Args:
            hash: Prompt hash
            
        Returns:
            Cached response if found, None otherwise
        """
        redis_client = await get_redis_client()
        cache_key = f"cache:exact:{hash}"
        
        try:
            cached_response = await redis_client.get(cache_key)
            if cached_response:
                logger.debug("L1 cache hit", hash=hash[:16])
                return cached_response
            else:
                logger.debug("L1 cache miss", hash=hash[:16])
                return None
        except Exception as e:
            logger.error("L1 cache check failed", hash=hash[:16], error=str(e))
            return None
    
    async def store(self, hash: str, response: str, ttl: int = None):
        """
        Store response in L1 cache.
        
        Args:
            hash: Prompt hash
            response: Model response
            ttl: Time to live in seconds (defaults to config value)
        """
        ttl = ttl or settings.L1_CACHE_TTL
        redis_client = await get_redis_client()
        cache_key = f"cache:exact:{hash}"
        
        try:
            await redis_client.setex(cache_key, ttl, response)
            logger.debug("L1 cache stored", hash=hash[:16], ttl=ttl)
        except Exception as e:
            logger.error("L1 cache store failed", hash=hash[:16], error=str(e))

