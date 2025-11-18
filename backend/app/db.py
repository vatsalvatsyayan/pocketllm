from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


logger = structlog.get_logger("backend-mongodb")

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        logger.info("connecting_to_mongodb", uri=settings.mongodb_uri)
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    global _database
    if _database is None:
        client = get_client()
        _database = client[settings.mongodb_db]
    return _database


async def health_check() -> bool:
    try:
        client = get_client()
        await client.admin.command("ping")
        return True
    except Exception as exc:  # pragma: no cover - best effort health check
        logger.warning("mongodb_ping_failed", error=str(exc))
        return False


@asynccontextmanager
async def lifespan(app):
    try:
        await health_check()
        database = get_database()
        from app.repositories.messages import MessageRepository
        from app.repositories.sessions import SessionRepository
        from app.repositories.users import UserRepository

        await UserRepository(database).ensure_indexes()
        await SessionRepository(database).ensure_indexes()
        await MessageRepository(database).ensure_indexes()
        yield
    finally:
        global _client, _database
        if _client:
            _client.close()
        _client = None
        _database = None


async def database_dependency() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    db = get_database()
    yield db