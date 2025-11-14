"""FastAPI application entry point."""
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.api import inference, metrics
from app.services.metrics import MetricsCollector


# Configure structured logging
import logging
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
        else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Model Management Service", version=settings.APP_VERSION)
    
    # Initialize metrics collector
    metrics_collector = MetricsCollector()
    app.state.metrics = metrics_collector
    
    # Start queue processor
    from app.services.queue_processor import QueueProcessor
    queue_processor = QueueProcessor(metrics_collector)
    await queue_processor.start()
    app.state.queue_processor = queue_processor
    
    yield
    
    # Stop queue processor
    if hasattr(app.state, "queue_processor"):
        await app.state.queue_processor.stop()
    
    logger.info("Shutting down Model Management Service")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Add CORS middleware
# Note: CORS middleware doesn't block WebSocket connections, but we configure it for HTTP requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.services.cache_manager import get_redis_client
    from app.services.database import get_db_session
    
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {},
    }
    
    # Check Redis
    try:
        redis_client = await get_redis_client()
        ping_result = await redis_client.ping()
        if ping_result:
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "unavailable (placeholder mode)"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["redis"] = f"unavailable (placeholder mode): {str(e)}"
        health_status["status"] = "degraded"
    
    # Check PostgreSQL
    try:
        from app.services.database import get_db_session, PlaceholderSession
        from sqlalchemy import text
        async for session in get_db_session():
            if isinstance(session, PlaceholderSession):
                health_status["checks"]["postgresql"] = "unavailable (placeholder mode)"
                health_status["status"] = "degraded"
            else:
                try:
                    # Quick test with timeout
                    import asyncio
                    await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=2.0)
                    health_status["checks"]["postgresql"] = "healthy"
                except asyncio.TimeoutError:
                    health_status["checks"]["postgresql"] = "unavailable (timeout)"
                    health_status["status"] = "degraded"
                except Exception as e:
                    health_status["checks"]["postgresql"] = f"unavailable: {str(e)}"
                    health_status["status"] = "degraded"
            break
    except Exception as e:
        health_status["checks"]["postgresql"] = f"unavailable (placeholder mode): {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Model Server (Ollama)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try /api/tags as health check for Ollama
            response = await client.get(f"{settings.MODEL_SERVER_URL}/api/tags")
            if response.status_code == 200:
                # Verify model is available
                tags_data = response.json()
                models = tags_data.get("models", [])
                model_names = [m.get("name", "") for m in models]
                if settings.MODEL_NAME in model_names or any(settings.MODEL_NAME in name for name in model_names):
                    health_status["checks"]["model_server"] = "healthy"
                    health_status["checks"]["model_name"] = settings.MODEL_NAME
                else:
                    health_status["checks"]["model_server"] = f"healthy (model {settings.MODEL_NAME} not found in available models)"
                    health_status["status"] = "degraded"
            else:
                health_status["checks"]["model_server"] = f"unhealthy: status {response.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["model_server"] = f"unavailable: {str(e)}"
        health_status["status"] = "degraded"
    
    # Service is still functional even if dependencies are unavailable (degraded mode)
    status_code = 200  # Always return 200, but indicate degraded status
    return JSONResponse(content=health_status, status_code=status_code)


# Include routers
app.include_router(inference.router, prefix="/api/v1", tags=["inference"])
app.include_router(metrics.router, prefix="/api/v1", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }

