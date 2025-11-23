from __future__ import annotations

from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings
from app.schemas.users import UserCreate
from app.utils.serializers import parse_object_id, to_public_id


def _public_user(document: dict) -> dict:
    user = to_public_id(document)
    name = user.get("full_name") or user.get("name") or user.get("email")
    user["name"] = name
    if "avatar_url" in user:
        user["avatar"] = user.get("avatar_url")
    user.pop("full_name", None)
    user.pop("avatar_url", None)
    # Ensure is_admin is included (defaults to False if not present)
    if "is_admin" not in user:
        user["is_admin"] = False
    return user


class UserRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection: AsyncIOMotorCollection = database[settings.users_collection]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("email", unique=True)

    async def create_user(self, payload: UserCreate, is_admin: bool = False) -> dict:
        now = datetime.utcnow()
        document = {
            "email": payload.email.lower(),
            "full_name": payload.name,
            "avatar_url": str(payload.avatar) if payload.avatar else None,
            "password_hash": payload.password_hash,
            "is_admin": is_admin,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return _public_user(document)
    
    async def update_user_admin_status(self, user_id: str, is_admin: bool) -> Optional[dict]:
        """Update a user's admin status."""
        object_id = parse_object_id(user_id)
        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": {"is_admin": is_admin, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            return None
        return await self.get_user(user_id)

    async def get_user(self, user_id: str) -> Optional[dict]:
        object_id = parse_object_id(user_id)
        document = await self.collection.find_one({"_id": object_id})
        if not document:
            return None
        return _public_user(document)

    async def list_users(self, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        cursor = (
            self.collection.find({})
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )
        documents = [_public_user(doc) async for doc in cursor]
        total = await self.collection.count_documents({})
        return documents, total

    async def find_by_email(self, email: str) -> Optional[dict]:
        document = await self.collection.find_one({"email": email.lower()})
        if not document:
            return None
        return _public_user(document)

    async def find_by_email_with_hash(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email.lower()})