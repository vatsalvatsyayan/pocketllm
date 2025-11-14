"""Queue processor background task."""
import asyncio
from typing import Optional
import structlog

from app.config import settings
from app.services.queue_manager import RequestQueue
from app.services.context_builder import ContextBuilder
from app.services.model_orchestrator import ModelOrchestrator
from app.services.response_handler import ResponseHandler
from app.services.cache_manager_service import CacheManager
from app.services.session_manager import SessionManager
from app.services.metrics import MetricsCollector

logger = structlog.get_logger()


class QueueProcessor:
    """Background task that processes requests from the queue."""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """Initialize queue processor."""
        self.queue = RequestQueue()
        self.context_builder = ContextBuilder()
        self.model_orchestrator = ModelOrchestrator()
        self.response_handler = ResponseHandler()
        self.cache_manager = CacheManager()
        self.session_manager = SessionManager()
        self.metrics = metrics_collector
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the queue processor."""
        if self._running:
            logger.warning("Queue processor already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._process_loop())
        logger.info("Queue processor started")
    
    async def stop(self):
        """Stop the queue processor."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Queue processor stopped")
    
    async def _process_loop(self):
        """Main processing loop."""
        while self._running:
            try:
                # Dequeue next request
                request = await self.queue.dequeue()
                
                if request:
                    # Process request (don't await - let it run in background)
                    asyncio.create_task(self._process_request(request))
                else:
                    # No requests, wait before checking again
                    await asyncio.sleep(settings.QUEUE_POLL_INTERVAL)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Queue processor error", error=str(e))
                await asyncio.sleep(settings.QUEUE_POLL_INTERVAL)
    
    async def _process_request(self, request):
        """Process a single request."""
        import time
        start_time = time.time()
        
        try:
            # Check cache first
            cache_result = await self.cache_manager.check_cache(
                request.prompt,
                request.config,  # Use config field (aliased as model_settings)
            )
            
            if cache_result:
                # Cache hit
                response_text, cache_type = cache_result
                cache_latency = (time.time() - start_time) * 1000
                
                if self.metrics:
                    self.metrics.record_cache_hit(cache_type)
                    self.metrics.record_latency(cache_latency, f"{cache_type}_cache")
                
                # Process response
                await self.response_handler.process_response(
                    response_text,
                    request.model_dump(),
                    cache_hit=True,
                    cache_type=cache_type,
                    latency_ms=cache_latency,
                    tokens_generated=0,  # TODO: Store token count in cache
                    tokens_prompt=0,
                )
                return
            
            # Cache miss - generate from model
            if self.metrics:
                self.metrics.record_cache_miss()
            
            # Load session
            messages = await self.session_manager.load_session(request.session_id)
            
            # Build context
            context = self.context_builder.build_context(messages, request.prompt)
            context = self.context_builder.truncate_if_needed(context, request.max_tokens)
            
            # Generate response
            model_config = {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }
            
            full_response = ""
            tokens_generated = 0
            
            async for chunk in self.model_orchestrator.generate_response(
                context,
                model_config,
                stream=False,  # Queue processing is non-streaming
            ):
                if chunk.get("done"):
                    full_response = chunk.get("full_response", "")
                    tokens_generated = chunk.get("tokens_generated", 0)
                    latency_ms = chunk.get("latency_ms", 0)
                    tokens_prompt = chunk.get("tokens_prompt", 0)
                    
                    # Process response
                    await self.response_handler.process_response(
                        full_response,
                        request.model_dump(),
                        cache_hit=False,
                        latency_ms=latency_ms,
                        tokens_generated=tokens_generated,
                        tokens_prompt=tokens_prompt,
                    )
                    
                    if self.metrics:
                        total_latency = (time.time() - start_time) * 1000
                        self.metrics.record_latency(total_latency, "total")
                        self.metrics.record_latency(latency_ms, "model")
            
        except Exception as e:
            logger.error("Request processing failed", error=str(e), session_id=request.session_id)

