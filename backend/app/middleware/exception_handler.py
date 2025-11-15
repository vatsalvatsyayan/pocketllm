from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import settings
import structlog

logger = structlog.get_logger("backend")


def register_exception_handler(app) -> None:
    @app.exception_handler(Exception)
    async def _global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled backend exception",
            path=request.url.path,
            method=request.method,
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal service error",
                "detail": "An unexpected issue occurred" if not settings.debug else str(exc),
            },
        )
