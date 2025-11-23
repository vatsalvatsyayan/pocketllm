"""Response handler - processes and stores responses."""
import asyncio
from typing import Dict, Any, Optional
import structlog
from datetime import datetime

from app.services.cache_manager_service import CacheManager
from app.services.session_manager import SessionManager
from app.models import InferenceResponse

logger = structlog.get_logger()


class ResponseHandler:
    """Handles response processing and storage."""
    
    def __init__(self):
        """Initialize response handler."""
        self.cache_manager = CacheManager()
        self.session_manager = SessionManager()
    
    async def process_response(
        self,
        response: str,
        request_data: Dict[str, Any],
        cache_hit: bool = False,
        cache_type: Optional[str] = None,
        latency_ms: float = 0.0,
        tokens_generated: int = 0,
        tokens_prompt: int = 0,
        context: Optional[str] = None,
        messages: Optional[list] = None,
    ) -> InferenceResponse:
        """
        Process response and store in caches and database.
        
        Args:
            response: Model response text
            request_data: Original request data
            cache_hit: Whether this was a cache hit
            cache_type: Cache type ("l1" or "l2")
            latency_ms: Response latency in milliseconds
            tokens_generated: Number of tokens generated
            tokens_prompt: Number of tokens in prompt
            
        Returns:
            InferenceResponse object
        """
        session_id = request_data.get("session_id")
        prompt = request_data.get("prompt")
        model_config = request_data.get("model_settings") or request_data.get("config")  # Support both aliases
        user_id = request_data.get("user_id")
        
        # Create response object
        inference_response = InferenceResponse(
            session_id=session_id,
            response=response,
            tokens_generated=tokens_generated,
            tokens_prompt=tokens_prompt,
            cache_hit=cache_hit,
            cache_type=cache_type,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow(),
        )
        
        # Store in parallel (non-blocking) with error tracking
        def log_task_error(task):
            """Log errors from background tasks."""
            try:
                task.result()
            except Exception as e:
                logger.error("Background task failed", error=str(e), exc_info=True)
        
        if not cache_hit:
            # Only cache if it wasn't a cache hit
            # Load messages if not provided (for context-aware caching)
            if messages is None and session_id:
                try:
                    messages = await self.session_manager.load_session(session_id)
                except Exception as e:
                    logger.warning("Failed to load messages for cache storage", error=str(e))
                    messages = []
            
            # Build context if not provided
            if context is None and messages:
                from app.services.context_builder import ContextBuilder
                context_builder = ContextBuilder()
                try:
                    context = context_builder.build_context(messages, prompt)
                except Exception as e:
                    logger.warning("Failed to build context for cache storage", error=str(e))
                    context = None
            
            task = asyncio.create_task(
                self._store_in_caches(prompt, response, model_config, context, messages)
            )
            task.add_done_callback(log_task_error)
        
        # Store message in database
        task = asyncio.create_task(
            self._store_message_in_db(
                session_id,
                "assistant",
                response,
                user_id,
            )
        )
        task.add_done_callback(log_task_error)
        
        # Update session cache
        task = asyncio.create_task(
            self._update_session_cache(session_id, "assistant", response)
        )
        task.add_done_callback(log_task_error)
        
        logger.info(
            "Response processed",
            session_id=session_id,
            cache_hit=cache_hit,
            cache_type=cache_type,
            tokens_generated=tokens_generated,
            latency_ms=latency_ms,
        )
        
        return inference_response
    
    async def _store_in_caches(
        self,
        prompt: str,
        response: str,
        model_config: Optional[Dict[str, Any]],
        context: Optional[str] = None,
        messages: Optional[list] = None,
    ):
        """Store response in L1 and L2 caches with context."""
        try:
            await self.cache_manager.store_in_cache(
                prompt, 
                response, 
                model_config,
                context=context,
                messages=messages,
            )
        except Exception as e:
            logger.error("Failed to store in caches", error=str(e))
    
    async def _store_message_in_db(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: Optional[str],
    ):
        """Store message in PostgreSQL database."""
        try:
            await self.session_manager.save_message_to_database(
                session_id,
                role,
                content,
                user_id,
            )
        except Exception as e:
            logger.error("Failed to store message in database", error=str(e))
    
    async def _update_session_cache(
        self,
        session_id: str,
        role: str,
        content: str,
    ):
        """Update session cache with new message."""
        try:
            messages = await self.session_manager.load_session(session_id)
            messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            })
            await self.session_manager.cache_session(session_id, messages)
        except Exception as e:
            logger.error("Failed to update session cache", error=str(e))

