from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = Field(default="New chat")
    metadata: dict | None = None


class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = Field(default="New chat")
    metadata: dict | None = None


class ChatSessionPublic(BaseModel):
    id: str
    user_id: str = Field(..., alias="userId")
    title: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_message_at: Optional[datetime] = Field(None, alias="lastMessageAt")
    last_message: Optional[str] = Field(None, alias="lastMessage")
    metadata: dict | None = None
    message_count: int = Field(0, alias="messageCount")

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda value: value.isoformat()}


class ChatSessionListResponse(BaseModel):
    data: list[ChatSessionPublic]
    total: int
    page: int
    limit: int
    has_more: bool = Field(..., alias="hasMore")

    class Config:
        populate_by_name = True