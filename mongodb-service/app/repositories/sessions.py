from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.config import settings
from app.schemas.sessions import ChatSessionCreate, Message, SessionMessageAppend
from app.utils.serializers import parse_object_id, to_public_id


def _public_session(document: dict) -> dict:
    doc = to_public_id(document)
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    doc["messages"] = doc.get("messages", [])
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
            "messages": [],
            "metadata": payload.metadata or {},
            "created_at": now,
            "updated_at": now,
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

    async def list_for_user(self, user_id: str, limit: int = 20, skip: int = 0) -> list[dict]:
        object_id = parse_object_id(user_id)
        cursor = (
            self.collection.find({"user_id": object_id})
            .skip(skip)
            .limit(limit)
            .sort("updated_at", -1)
        )
        return [_public_session(doc) async for doc in cursor]

    async def append_message(self, session_id: str, payload: SessionMessageAppend) -> Optional[dict]:
        object_id = parse_object_id(session_id)
        message = payload.message.model_dump()
        if not message.get("created_at"):
            message["created_at"] = datetime.utcnow()
        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$push": {"messages": message}, "$set": {"updated_at": datetime.utcnow()}},
            return_document=ReturnDocument.AFTER,
        )
        if not result:
            return None
        return _public_session(result)

    async def delete_session(self, session_id: str) -> bool:
        object_id = parse_object_id(session_id)
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1

