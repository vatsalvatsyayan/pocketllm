from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings
from app.schemas.users import UserCreate
from app.utils.serializers import parse_object_id, to_public_id


class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = database[settings.users_collection]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("email", unique=True)

    async def create_user(self, payload: UserCreate) -> dict:
        now = datetime.utcnow()
        document = {
            "email": payload.email.lower(),
            "full_name": payload.full_name,
            "avatar_url": str(payload.avatar_url) if payload.avatar_url else None,
            "password_hash": payload.password_hash,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return to_public_id(document)

    async def get_user(self, user_id: str) -> Optional[dict]:
        object_id = parse_object_id(user_id)
        document = await self.collection.find_one({"_id": object_id})
        if not document:
            return None
        return to_public_id(document)

    async def list_users(self, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        cursor = (
            self.collection.find({})
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )
        documents = [to_public_id(doc) async for doc in cursor]
        total = await self.collection.count_documents({})
        return documents, total

    async def find_by_email(self, email: str) -> Optional[dict]:
        document = await self.collection.find_one({"email": email.lower()})
        if not document:
            return None
        return to_public_id(document)

