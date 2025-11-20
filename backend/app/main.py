"""FastAPI backend entry point for the pocketLLM middleware service."""
from __future__ import annotations

import logging
import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware import (
    configure_cors,
    configure_rate_limit,
    get_authenticator,
    register_exception_handler,
)
from app.routers import router as api_router
from app.routers.chat import router as chat_router
from app.db import lifespan


log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    context_class=dict,
    wrapper_class=structlog.make_filtering_bound_logger(log_level),
)
logger = structlog.get_logger("backend")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

configure_cors(app)
configure_rate_limit(app)
register_exception_handler(app)

authenticator = get_authenticator()
app.state.authenticator = authenticator

app.include_router(api_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc: RateLimitExceeded):
    logger.warning(
        "rate_limit_exceeded",
        path=request.url.path,
        method=request.method,
        detail=str(exc.detail),
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "detail": str(exc.detail),
        },
    )


@app.get("/")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }