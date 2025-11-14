"""Model orchestrator - coordinates generation and streaming."""
import asyncio
from typing import Optional, Dict, Any, AsyncIterator
import structlog
from datetime import datetime

from app.services.model_client import ModelClient
from app.utils.token_counter import count_tokens

logger = structlog.get_logger()


class ModelOrchestrator:
    """Orchestrates model generation and streaming."""
    
    def __init__(self):
        """Initialize model orchestrator."""
        self.model_client = ModelClient()
        self._active_tasks: Dict[str, asyncio.Task] = {}
    
    async def generate_response(
        self,
        context: str,
        config: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        stream: bool = True,
        cancellation_token: Optional[asyncio.Task] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate response from model with streaming support.
        
        Args:
            context: Formatted context string
            config: Model configuration
            user_id: User identifier
            stream: Whether to stream tokens
            cancellation_token: Optional cancellation token
            
        Yields:
            Dictionary with token data: {"token": str, "done": bool}
        """
        start_time = datetime.utcnow()
        tokens_generated = 0
        full_response = ""
        
        try:
            if stream:
                async for token in self.model_client.stream_completion(
                    context,
                    config,
                    cancellation_token,
                ):
                    tokens_generated += 1
                    full_response += token
                    
                    yield {
                        "token": token,
                        "done": False,
                        "tokens_generated": tokens_generated,
                    }
            else:
                # Non-streaming mode
                response = await self.model_client.get_completion(context, config)
                tokens_generated = count_tokens(response)
                full_response = response
                
                yield {
                    "token": response,
                    "done": True,
                    "tokens_generated": tokens_generated,
                }
            
            # Final yield with completion
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            yield {
                "token": "",
                "done": True,
                "tokens_generated": tokens_generated,
                "full_response": full_response,
                "latency_ms": latency_ms,
                "tokens_prompt": count_tokens(context),
            }
            
        except Exception as e:
            logger.error("Model generation failed", error=str(e), user_id=user_id)
            yield {
                "token": "",
                "done": True,
                "error": str(e),
            }
    
    def create_cancellation_token(self, request_id: str) -> asyncio.Task:
        """
        Create a cancellation token for a request.
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            Cancellation task
        """
        # Clean up old tasks to prevent memory leak
        if len(self._active_tasks) > 1000:
            logger.warning("Too many active tasks, cleaning up", count=len(self._active_tasks))
            # Remove completed tasks
            completed = [rid for rid, task in self._active_tasks.items() if task.done()]
            for rid in completed:
                del self._active_tasks[rid]
        
        cancellation_task = asyncio.create_task(asyncio.sleep(float('inf')))
        self._active_tasks[request_id] = cancellation_task
        return cancellation_task
    
    def cancel_request(self, request_id: str) -> bool:
        """
        Cancel an active request.
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            True if cancelled, False if not found
        """
        if request_id in self._active_tasks:
            task = self._active_tasks[request_id]
            task.cancel()
            del self._active_tasks[request_id]
            logger.info("Request cancelled", request_id=request_id)
            return True
        return False

