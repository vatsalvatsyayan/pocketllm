from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings
from app.schemas.messages import MessageCreate, MessageRead
from app.utils.serializers import parse_object_id, to_public_id


def _public_message(document: dict) -> dict:
    doc = to_public_id(document)
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    if "session_id" in doc:
        doc["session_id"] = str(doc["session_id"])
    return doc


class MessageRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = database[settings.messages_collection]
        self.sessions: AsyncIOMotorCollection = database[settings.sessions_collection]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index([("session_id", 1), ("created_at", 1)])
        await self.collection.create_index([("user_id", 1)])

    async def list_messages(
        self,
        session_id: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[dict]:
        session_obj_id = parse_object_id(session_id)
        user_obj_id = parse_object_id(user_id)
        cursor = (
            self.collection
            .find({"session_id": session_obj_id, "user_id": user_obj_id})
            .sort("created_at", 1)
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [_public_message(doc) for doc in docs]

    async def create_message(
        self,
        session_id: str,
        user_id: str,
        payload: MessageCreate,
    ) -> dict:
        now = datetime.utcnow()
        session_obj_id = parse_object_id(session_id)
        user_obj_id = parse_object_id(user_id)

        # Insert message
        doc = {
            "session_id": session_obj_id,
            "user_id": user_obj_id,
            "role": payload.role,
            "content": payload.content,
            "created_at": now,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id

        # Update session's last_message_at + updated_at
        await self.sessions.update_one(
            {"_id": session_obj_id, "user_id": user_obj_id},
            {
                "$set": {
                    "last_message_at": now,
                    "updated_at": now,
                    "last_message": payload.content,
                },
                "$inc": {"message_count": 1},
            },
        )

        return _public_message(doc)
