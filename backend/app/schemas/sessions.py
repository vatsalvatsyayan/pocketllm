from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    user_id: str
    title: Optional[str] = Field(default="New chat")
    metadata: dict | None = None


class ChatSessionPublic(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    metadata: dict | None = None