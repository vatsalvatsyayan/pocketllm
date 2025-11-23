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
        from app.utils.security import hash_password
        from datetime import datetime

        await UserRepository(database).ensure_indexes()
        await SessionRepository(database).ensure_indexes()
        await MessageRepository(database).ensure_indexes()
        
        # Create demo user if it doesn't exist
        user_repo = UserRepository(database)
        demo_email = "demo@pocketllm.com"
        existing_user = await user_repo.find_by_email(demo_email)
        if not existing_user:
            from app.schemas.users import UserCreate
            password_hash = hash_password("demo123")
            await user_repo.create_user(
                UserCreate(
                    email=demo_email,
                    name="Demo User",
                    avatar=None,
                    password_hash=password_hash,
                )
            )
            logger.info("Demo user created", email=demo_email)
        else:
            logger.debug("Demo user already exists", email=demo_email)
        
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