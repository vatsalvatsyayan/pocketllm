from __future__ import annotations

import logging

import structlog
from fastapi import FastAPI

from app.config import settings
from app.db import health_check, lifespan
from app.routers import router as api_router


def configure_logging() -> None:
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
    )


configure_logging()
logger = structlog.get_logger("mongodb-service")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    alive = await health_check()
    status = "ok" if alive else "degraded"
    return {
        "status": status,
        "service": settings.app_name,
        "version": settings.app_version,
    }

