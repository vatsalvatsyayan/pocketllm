from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class MessageRead(BaseModel):
    id: str
    session_id: str
    user_id: str
    role: str
    content: str
    created_at: datetime


class ChatStreamRequest(BaseModel):
    session_id: str = Field(..., alias="sessionId")
    prompt: str
    message_id: Optional[str] = Field(None, alias="messageId")
