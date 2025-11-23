"""Inference API endpoints."""
from fastapi import APIRouter, Request, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Optional
import structlog
import asyncio
import time
import json
from contextlib import asynccontextmanager

from app.models import InferenceRequest, InferenceResponse, WebSocketMessage
from app.services.cache_manager_service import CacheManager
from app.services.session_manager import SessionManager
from app.services.context_builder import ContextBuilder
from app.services.model_orchestrator import ModelOrchestrator
from app.services.response_handler import ResponseHandler
from app.services.queue_manager import RequestQueue
from app.services.metrics import MetricsCollector
from app.config import settings

logger = structlog.get_logger()

router = APIRouter()

# Service instances
cache_manager = CacheManager()
session_manager = SessionManager()
context_builder = ContextBuilder()
model_orchestrator = ModelOrchestrator()
response_handler = ResponseHandler()
queue = RequestQueue()


@router.post("/inference/chat", response_model=InferenceResponse)
async def chat_endpoint(
    request: InferenceRequest,
    http_request: Request,
):
    """
    Non-streaming chat endpoint with cancellation support.
    Processes request synchronously and returns complete response.
    """
    start_time = time.time()
    session_id = request.session_id
    prompt = request.prompt
    
    # Fix race condition: Save user prompt BEFORE loading history
    try:
        await session_manager.save_message_to_database(
            session_id,
            "user",
            prompt,
            user_id=None
        )
    except Exception as e:
        logger.warning("Failed to save user prompt to database", session_id=session_id, error=str(e))
        # Continue anyway - prompt will be in context
    
    # Load session history - use messages from request if provided, otherwise load from database
    if request.messages:
        # Use messages provided by backend (from MongoDB)
        messages = request.messages
        logger.debug("Using messages from request", session_id=session_id, message_count=len(messages))
    else:
        # Fall back to loading from database (PostgreSQL)
        try:
            messages = await session_manager.load_session(session_id)
            logger.debug("Loaded messages from database", session_id=session_id, message_count=len(messages))
        except Exception as e:
            logger.warning("Failed to load session history", session_id=session_id, error=str(e))
            messages = []
    
    # Build context - this is needed for accurate cache key generation
    # IMPORTANT: Build FULL context first (before truncation) for accurate cache keys
    full_context = None
    context = None
    try:
        if messages:
            # Build full context first - use this for cache key generation
            full_context = context_builder.build_context(messages, prompt)
            
            # Truncate context only for model input (after cache check)
            # Use MAX_CONTEXT_TOKENS for input context (not max_tokens which is for response)
            max_context_tokens = settings.MAX_CONTEXT_TOKENS
            original_context_length = len(full_context)
            context = context_builder.truncate_if_needed(full_context, max_context_tokens)
            truncated_length = len(context)
            
            logger.info(
                "Context built for model",
                session_id=session_id,
                message_count=len(messages),
                original_length=original_context_length,
                truncated_length=truncated_length,
                max_context_tokens=max_context_tokens,
                was_truncated=original_context_length != truncated_length,
            )
        else:
            full_context = prompt
            context = prompt
            logger.debug("No message history, using prompt only", session_id=session_id)
    except Exception as e:
        logger.error("Failed to build context", session_id=session_id, error=str(e))
        full_context = prompt  # Fallback to prompt only
        context = prompt  # Fallback to prompt only
    
    # Check cache AFTER building full context - use FULL context (not truncated) for accurate cache key
    # This ensures same prompt in different conversation contexts gets different cache keys
    model_config = request.config or {"temperature": request.temperature, "max_tokens": request.max_tokens}
    cache_result = await cache_manager.check_cache(
        prompt,
        model_config,
        context=full_context,  # Pass FULL context (before truncation) for accurate cache key
        messages=messages,  # Also pass messages as fallback
    )
    
    if cache_result:
        # Cache hit
        response_text, cache_type = cache_result
        latency_ms = (time.time() - start_time) * 1000
        
        # Process response
        request_data = request.model_dump()
        await response_handler.process_response(
            response_text,
            request_data,
            cache_hit=True,
            cache_type=cache_type,
            latency_ms=latency_ms,
            tokens_generated=0,
            tokens_prompt=0,
        )
        
        return InferenceResponse(
            session_id=session_id,
            response=response_text,
            tokens_generated=0,
            tokens_prompt=0,
            cache_hit=True,
            cache_type=cache_type,
            latency_ms=latency_ms,
        )
    
    # Cache miss - generate from model
    
    # Generate response (non-streaming)
    # model_config already defined above
    
    full_response = ""
    tokens_generated = 0
    tokens_prompt = 0
    latency_ms = 0.0
    generation_error = None
    
    try:
        async for chunk in model_orchestrator.generate_response(
            context,
            model_config,
            user_id=None,
            stream=False,  # Non-streaming
            cancellation_token=None,
        ):
            if not chunk:
                logger.warning("Received None chunk from model orchestrator", session_id=session_id)
                continue
            
            if chunk.get("done"):
                # Check for errors first
                if "error" in chunk:
                    generation_error = chunk.get("error")
                    logger.error("Model generation error", session_id=session_id, error=generation_error)
                    break
                
                full_response = chunk.get("full_response") or chunk.get("token") or ""
                tokens_generated = chunk.get("tokens_generated", 0)
                tokens_prompt = chunk.get("tokens_prompt", 0)
                latency_ms = chunk.get("latency_ms", (time.time() - start_time) * 1000)
                break
        
        # If we got an error, raise HTTPException
        if generation_error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Model generation failed: {generation_error}"
            )
        
        # Validate we got a response
        if not full_response and not generation_error:
            logger.warning("No response generated", session_id=session_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model generated empty response"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Model generation failed", session_id=session_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model generation failed: {str(e)}"
        )
    
    # Process response (non-blocking background tasks)
    request_data = request.model_dump()
    try:
        await response_handler.process_response(
            full_response,
            request_data,
            cache_hit=False,
            latency_ms=latency_ms,
            tokens_generated=tokens_generated,
            tokens_prompt=tokens_prompt,
            context=context,  # Pass context for cache storage
            messages=messages,  # Pass messages for cache storage
        )
    except Exception as e:
        logger.error("Failed to process response", session_id=session_id, error=str(e))
        # Don't fail the request if response processing fails
    
    return InferenceResponse(
        session_id=session_id,
        response=full_response,
        tokens_generated=tokens_generated,
        tokens_prompt=tokens_prompt,
        cache_hit=False,
        latency_ms=latency_ms,
    )


@router.post("/inference/chat/stream")
async def chat_stream_endpoint(
    request: InferenceRequest,
    http_request: Request,
):
    """
    Streaming chat endpoint.
    Returns Server-Sent Events (SSE) stream of tokens.
    """
    async def generate_stream():
        session_id = request.session_id
        prompt = request.prompt
        
        # Fix race condition: Save user prompt BEFORE loading history
        try:
            await session_manager.save_message_to_database(
                session_id,
                "user",
                prompt,
                user_id=None
            )
        except Exception as e:
            logger.warning("Failed to save user prompt to database", session_id=session_id, error=str(e))
            # Continue anyway - prompt will be in context
        
        # Load session history - use messages from request if provided, otherwise load from database
        if request.messages:
            # Use messages provided by backend (from MongoDB)
            messages = request.messages
            logger.debug("Using messages from request (streaming)", session_id=session_id, message_count=len(messages))
        else:
            # Fall back to loading from database (PostgreSQL)
            try:
                messages = await session_manager.load_session(session_id)
                logger.debug("Loaded messages from database (streaming)", session_id=session_id, message_count=len(messages))
            except Exception as e:
                logger.warning("Failed to load session history", session_id=session_id, error=str(e))
                messages = []
        
        # Build context - this is needed for accurate cache key generation
        # IMPORTANT: Build FULL context first (before truncation) for accurate cache keys
        full_context = None
        context = None
        try:
            if messages:
                # Build full context first - use this for cache key generation
                full_context = context_builder.build_context(messages, prompt)
                
                # Truncate context only for model input (after cache check)
                # Use MAX_CONTEXT_TOKENS for input context (not max_tokens which is for response)
                max_context_tokens = settings.MAX_CONTEXT_TOKENS
                original_context_length = len(full_context)
                context = context_builder.truncate_if_needed(full_context, max_context_tokens)
                truncated_length = len(context)
                
                logger.info(
                    "Context built for model (streaming)",
                    session_id=session_id,
                    message_count=len(messages),
                    original_length=original_context_length,
                    truncated_length=truncated_length,
                    max_context_tokens=max_context_tokens,
                    was_truncated=original_context_length != truncated_length,
                )
            else:
                full_context = prompt
                context = prompt
                logger.debug("No message history, using prompt only (streaming)", session_id=session_id)
        except Exception as e:
            logger.error("Failed to build context", session_id=session_id, error=str(e))
            full_context = prompt  # Fallback to prompt only
            context = prompt  # Fallback to prompt only
        
        # Check cache AFTER building full context - use FULL context (not truncated) for accurate cache key
        # This ensures same prompt in different conversation contexts gets different cache keys
        model_config = request.config or {"temperature": request.temperature, "max_tokens": request.max_tokens}
        cache_result = await cache_manager.check_cache(
            prompt,
            model_config,
            context=full_context,  # Pass FULL context (before truncation) for accurate cache key
            messages=messages,  # Also pass messages as fallback
        )
        
        if cache_result:
            # Cache hit - send as single chunk
            response_text, cache_type = cache_result
            yield f"data: {json.dumps({'token': response_text, 'done': True, 'cache_hit': True, 'cache_type': cache_type})}\n\n"
            
            # Process response
            request_data = request.model_dump()
            await response_handler.process_response(
                response_text,
                request_data,
                cache_hit=True,
                cache_type=cache_type,
                latency_ms=0.0,
                tokens_generated=0,
                tokens_prompt=0,
            )
            return
        
        # Cache miss - generate from model
        
        # Generate response with streaming
        # model_config already defined above
        
        full_response = ""
        tokens_generated = 0
        tokens_prompt = 0
        latency_ms = 0.0
        generation_error = None
        
        try:
            async for chunk in model_orchestrator.generate_response(
                context,
                model_config,
                user_id=None,
                stream=True,
                cancellation_token=None,
            ):
                if not chunk:
                    logger.warning("Received None chunk from model orchestrator", session_id=session_id)
                    continue
                
                if chunk.get("done"):
                    # Check for errors first
                    if "error" in chunk:
                        generation_error = chunk.get("error")
                        logger.error("Model generation error", session_id=session_id, error=generation_error)
                        yield f"data: {json.dumps({'token': '', 'done': True, 'error': generation_error})}\n\n"
                        return
                    
                    full_response = chunk.get("full_response", "")
                    tokens_generated = chunk.get("tokens_generated", 0)
                    tokens_prompt = chunk.get("tokens_prompt", 0)
                    latency_ms = chunk.get("latency_ms", 0.0)
                    
                    # Send completion event
                    yield f"data: {json.dumps({'token': '', 'done': True, 'tokens_generated': tokens_generated, 'tokens_prompt': tokens_prompt, 'latency_ms': latency_ms})}\n\n"
                    
                    # Process response (non-blocking)
                    request_data = request.model_dump()
                    try:
                        await response_handler.process_response(
                            full_response,
                            request_data,
                            cache_hit=False,
                            latency_ms=latency_ms,
                            tokens_generated=tokens_generated,
                            tokens_prompt=tokens_prompt,
                            context=context,  # Pass context for cache storage
                            messages=messages,  # Pass messages for cache storage
                        )
                    except Exception as e:
                        logger.error("Failed to process response", session_id=session_id, error=str(e))
                    return
                else:
                    # Send token
                    token = chunk.get("token", "")
                    if token:
                        full_response += token
                        yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
        
        except Exception as e:
            logger.error("Stream generation failed", session_id=session_id, error=str(e), exc_info=True)
            yield f"data: {json.dumps({'token': '', 'done': True, 'error': str(e)})}\n\n"
            return
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming inference.
    """
    await websocket.accept()
    
    try:
        cancellation_token = None
        
        while True:
            # Receive message
            try:
                data = await websocket.receive_json()
                message = WebSocketMessage(**data)
            except Exception as e:
                logger.warning("Invalid WebSocket message", error=str(e))
                await websocket.send_json({
                    "event": "stream_error",
                    "data": {"error": "Invalid message format"},
                })
                continue
            
            # Handle different event types
            if message.event == "stream_chat":
                # Start streaming chat
                request_data = message.data
                session_id = request_data.get("session_id")
                prompt = request_data.get("prompt")
                stream = request_data.get("stream", True)
                
                if not session_id or not prompt:
                    await websocket.send_json({
                        "event": "stream_error",
                        "data": {"error": "Missing session_id or prompt"},
                    })
                    continue
                
                # Create cancellation token
                cancellation_token = model_orchestrator.create_cancellation_token(session_id)
                
                # Load session history - use messages from request if provided, otherwise load from database
                messages = request_data.get("messages")
                if messages:
                    # Use messages provided by backend (from MongoDB)
                    logger.debug("Using messages from request (WebSocket)", session_id=session_id, message_count=len(messages))
                else:
                    # Fall back to loading from database (PostgreSQL)
                    try:
                        messages = await session_manager.load_session(session_id)
                        logger.debug("Loaded messages from database (WebSocket)", session_id=session_id, message_count=len(messages))
                    except Exception as e:
                        logger.warning("Failed to load session history", session_id=session_id, error=str(e))
                        messages = []
                
                # Save user prompt to database (non-blocking, after loading history)
                asyncio.create_task(
                    session_manager.save_message_to_database(
                        session_id,
                        "user",
                        prompt,
                        user_id=None
                    )
                )
                
                # Build context - needed for accurate cache key generation
                # IMPORTANT: Build FULL context first (before truncation) for accurate cache keys
                full_context = None
                context = None
                try:
                    if messages:
                        # Build full context first - use this for cache key generation
                        full_context = context_builder.build_context(messages, prompt)
                        
                        # Truncate context only for model input (after cache check)
                        max_context_tokens = settings.MAX_CONTEXT_TOKENS
                        context = context_builder.truncate_if_needed(full_context, max_context_tokens)
                    else:
                        full_context = prompt
                        context = prompt
                except Exception as e:
                    logger.error("Failed to build context", session_id=session_id, error=str(e))
                    full_context = prompt  # Fallback to prompt only
                    context = prompt  # Fallback to prompt only
                
                # Check cache AFTER building full context - use FULL context (not truncated) for accurate cache key
                start_time = time.time()
                model_config = request_data.get("model_settings") or request_data.get("config")
                cache_result = await cache_manager.check_cache(
                    prompt,
                    model_config,
                    context=full_context,  # Pass FULL context (before truncation) for accurate cache key
                    messages=messages,  # Also pass messages as fallback
                )
                
                if cache_result:
                    # Cache hit - send immediately
                    response_text, cache_type = cache_result
                    cache_latency = (time.time() - start_time) * 1000
                    
                    # Send cached response as single token
                    await websocket.send_json({
                        "event": "stream_token",
                        "data": {"token": response_text},
                    })
                    
                    await websocket.send_json({
                        "event": "stream_complete",
                        "data": {
                            "cache_hit": True,
                            "cache_type": cache_type,
                            "latency_ms": cache_latency,
                        },
                    })
                    
                    # Process response
                    await response_handler.process_response(
                        response_text,
                        request_data,
                        cache_hit=True,
                        cache_type=cache_type,
                        latency_ms=cache_latency,
                        tokens_generated=0,
                        tokens_prompt=0,
                    )
                    continue
                
                # Cache miss - generate from model
                # Context already built above for cache check
                # model_config already defined above
                
                full_response = ""
                tokens_generated = 0
                generation_start = time.time()
                
                async for chunk in model_orchestrator.generate_response(
                    context,
                    model_config,
                    user_id=None,  # No user_id needed without auth
                    stream=True,
                    cancellation_token=cancellation_token,
                ):
                    if chunk.get("done"):
                        # Generation complete
                        full_response = chunk.get("full_response", "")
                        tokens_generated = chunk.get("tokens_generated", 0)
                        latency_ms = chunk.get("latency_ms", 0)
                        tokens_prompt = chunk.get("tokens_prompt", 0)
                        
                        await websocket.send_json({
                            "event": "stream_complete",
                            "data": {
                                "cache_hit": False,
                                "tokens_generated": tokens_generated,
                                "tokens_prompt": tokens_prompt,
                                "latency_ms": latency_ms,
                            },
                        })
                        
                        # Process response
                        await response_handler.process_response(
                            full_response,
                            request_data,
                            cache_hit=False,
                            latency_ms=latency_ms,
                            tokens_generated=tokens_generated,
                            tokens_prompt=tokens_prompt,
                            context=context,  # Pass context for cache storage
                            messages=messages,  # Pass messages for cache storage
                        )
                    else:
                        # Send token
                        token = chunk.get("token", "")
                        if token:
                            full_response += token
                            tokens_generated = chunk.get("tokens_generated", 0)
                            
                            await websocket.send_json({
                                "event": "stream_token",
                                "data": {"token": token},
                            })
            
            elif message.event == "stop_generation":
                # Stop generation
                session_id = message.data.get("session_id")
                if session_id:
                    model_orchestrator.cancel_request(session_id)
                    await websocket.send_json({
                        "event": "stream_complete",
                        "data": {"stopped": True},
                    })
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        try:
            await websocket.send_json({
                "event": "stream_error",
                "data": {"error": str(e)},
            })
        except:
            pass
    finally:
        # Clean up cancellation token
        if cancellation_token:
            cancellation_token.cancel()

