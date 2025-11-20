from __future__ import annotations

from datetime import datetime
from typing import Literal

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
