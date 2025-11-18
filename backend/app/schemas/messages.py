from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.utils.serializers import parse_object_id


class MessageBase(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Message role")
    content: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: str
    session_id: str
    user_id: str
    created_at: datetime
