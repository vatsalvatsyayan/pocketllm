"""Model client for communicating with Ollama server."""
import asyncio
from typing import AsyncIterator, Optional, Dict, Any
import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


class ModelClient:
    """HTTP client for Ollama model server."""
    
    def __init__(self):
        """Initialize model client."""
        self.base_url = settings.MODEL_SERVER_URL
        self.timeout = settings.MODEL_SERVER_TIMEOUT
        self.max_retries = settings.MODEL_MAX_RETRIES
        self.retry_delay = settings.MODEL_RETRY_DELAY
    
    async def stream_completion(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        cancellation_token: Optional[asyncio.Task] = None,
    ) -> AsyncIterator[str]:
        """
        Stream completion from model server.
        
        Args:
            prompt: Input prompt
            config: Model configuration (temperature, max_tokens, etc.)
            cancellation_token: Optional cancellation token to stop streaming
            
        Yields:
            Token strings as they are generated
            
        Raises:
            httpx.HTTPError: If request fails after retries
        """
        config = config or {}
        
        # Prepare request payload (Ollama API format)
        from app.config import settings
        payload = {
            "model": config.get("model", settings.MODEL_NAME),
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": config.get("temperature", 0.7),
            }
        }
        
        # Add max_tokens if provided
        if config.get("max_tokens"):
            payload["options"]["num_predict"] = config.get("max_tokens")
        
        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/api/generate",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            raise httpx.HTTPError(
                                f"Model server returned {response.status_code}: {error_text.decode()}"
                            )
                        
                        # Stream Server-Sent Events (SSE)
                        async for line in response.aiter_lines():
                            # Check for cancellation
                            if cancellation_token and cancellation_token.done():
                                logger.info("Stream cancelled by user")
                                return
                            
                            # Parse Ollama streaming format (JSON lines)
                            if line.strip():
                                try:
                                    import json
                                    data = json.loads(line)
                                    
                                    # Ollama format: {"response": "token", "done": false}
                                    token = data.get("response", "")
                                    done = data.get("done", False)
                                    
                                    if token:
                                        yield token
                                    
                                    if done:
                                        logger.debug("Stream completed")
                                        return
                                except json.JSONDecodeError:
                                    logger.warning("Failed to parse JSON line", data=line)
                                    continue
                            
                            # Check for errors in JSON response
                            if line.strip():
                                try:
                                    import json
                                    data = json.loads(line)
                                    if "error" in data:
                                        error_msg = data.get("error", "Unknown error")
                                        logger.error("Model server error", error=error_msg)
                                        raise httpx.HTTPError(f"Model server error: {error_msg}")
                                except json.JSONDecodeError:
                                    pass
                        
                        # Stream completed successfully
                        return
                        
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(
                    "Model request failed",
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(e),
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        else:
            raise httpx.HTTPError("Model request failed after retries")
    
    async def get_completion(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get non-streaming completion from model server.
        
        Args:
            prompt: Input prompt
            config: Model configuration
            
        Returns:
            Complete response text
        """
        config = config or {}
        
        # Prepare request payload (Ollama API format)
        from app.config import settings
        payload = {
            "model": config.get("model", settings.MODEL_NAME),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.get("temperature", 0.7),
            }
        }
        
        # Add max_tokens if provided
        if config.get("max_tokens"):
            payload["options"]["num_predict"] = config.get("max_tokens")
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Ollama format: {"response": "full text"}
                        return data.get("response", "")
                    else:
                        raise httpx.HTTPError(
                            f"Model server returned {response.status_code}: {response.text}"
                        )
                        
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise
        
        raise httpx.HTTPError("Model request failed after retries")

