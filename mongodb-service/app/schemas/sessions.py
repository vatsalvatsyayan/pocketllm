from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = Field(default="New chat")
    metadata: dict | None = None


class ChatSessionPublic(BaseModel):
    id: str
    user_id: str
    title: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime
    metadata: dict | None = None


class SessionMessageAppend(BaseModel):
    message: Message

