from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class UserCreate(UserBase):
    password_hash: str = Field(..., min_length=32, description="Pre-hashed password")


class UserPublic(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    items: list[UserPublic]
    total: int

