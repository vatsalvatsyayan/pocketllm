"""Database connection utilities."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Optional
import structlog

from app.config import settings

logger = structlog.get_logger()

# Global engine - None if DB unavailable
engine: Optional[object] = None
AsyncSessionLocal: Optional[async_sessionmaker] = None

# Base class for models
Base = declarative_base()


class PlaceholderSession:
    """Placeholder database session for when DB is unavailable."""
    
    async def execute(self, *args, **kwargs):
        return None
    
    async def commit(self):
        pass
    
    async def rollback(self):
        pass
    
    async def close(self):
        pass


def _init_db_engine():
    """Initialize database engine with error handling - non-blocking."""
    global engine, AsyncSessionLocal
    
    if engine is not None:
        return
    
    # If DATABASE_URL is empty or invalid, use placeholder mode
    if not settings.DATABASE_URL or settings.DATABASE_URL.strip() == "":
        logger.info("DATABASE_URL not set, using placeholder mode")
        engine = None
        AsyncSessionLocal = None
        return
    
    try:
        # Create engine with connection pool that doesn't validate on creation
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,  # Only check on use, not on creation
            pool_size=5,  # Smaller pool
            max_overflow=10,
            pool_timeout=2,  # Short timeout
            connect_args={
                "server_settings": {"application_name": "model_management"},
                "command_timeout": 2,  # Connection timeout
            },
        )
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        # Mark as available - actual connection will be tested on first use
        logger.info("Database engine initialized (lazy connection)", url=settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "unknown")
    except Exception as e:
        logger.warning("Database initialization failed, using placeholder mode", error=str(e))
        engine = None
        AsyncSessionLocal = None


async def get_db_session() -> AsyncGenerator[Optional[AsyncSession], None]:
    """
    Get database session with graceful fallback.
    
    Yields:
        AsyncSession instance or PlaceholderSession if DB unavailable
    """
    _init_db_engine()
    
    if AsyncSessionLocal is None:
        logger.debug("Database unavailable, using placeholder mode")
        yield PlaceholderSession()
        return
    
    try:
        async with AsyncSessionLocal() as session:
            try:
                # Don't test connection here - just yield the session
                # Connection will be tested when actually used
                yield session
                # Only commit if no exception occurred
                try:
                    await session.commit()
                except Exception as commit_error:
                    logger.warning("Database commit failed", error=str(commit_error))
                    await session.rollback()
                    raise
            except Exception as e:
                logger.warning("Database operation failed", error=str(e))
                try:
                    await session.rollback()
                except Exception as rollback_error:
                    logger.warning("Database rollback failed", error=str(rollback_error))
                # Don't yield placeholder here - let the exception propagate
                raise
            finally:
                try:
                    await session.close()
                except Exception as close_error:
                    logger.warning("Database close failed", error=str(close_error))
    except Exception as e:
        logger.warning("Database connection failed, using placeholder", error=str(e))
        yield PlaceholderSession()

