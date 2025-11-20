from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings
from app.schemas.sessions import ChatSessionCreate
from app.utils.serializers import parse_object_id, to_public_id


def _public_session(document: dict) -> dict:
    doc = to_public_id(document)
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    doc["message_count"] = int(doc.get("message_count", 0) or 0)
    return doc


class SessionRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = database[settings.sessions_collection]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index([("user_id", 1), ("created_at", -1)])

    async def create_session(self, payload: ChatSessionCreate) -> dict:
        now = datetime.utcnow()
        document = {
            "user_id": parse_object_id(payload.user_id),
            "title": payload.title or "New chat",
            "metadata": payload.metadata or {},
            "created_at": now,
            "updated_at": now,
            "last_message_at": None,
            "message_count": 0,
        }
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return _public_session(document)

    async def get_session(self, session_id: str) -> Optional[dict]:
        object_id = parse_object_id(session_id)
        document = await self.collection.find_one({"_id": object_id})
        if not document:
            return None
        return _public_session(document)

    async def list_for_user(
        self,
        user_id: str,
        limit: int = 20,
        skip: int = 0,
        sort_field: str = "updated_at",
        sort_direction: int = -1,
    ) -> list[dict]:
        object_id = parse_object_id(user_id)
        cursor = (
            self.collection
            .find({"user_id": object_id})
            .sort(sort_field, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        return [_public_session(doc) async for doc in cursor]

    async def count_for_user(self, user_id: str) -> int:
        object_id = parse_object_id(user_id)
        return await self.collection.count_documents({"user_id": object_id})


    async def delete_session(self, session_id: str) -> bool:
        object_id = parse_object_id(session_id)
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1