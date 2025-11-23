from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = Field(None, alias="full_name")
    avatar: Optional[HttpUrl] = Field(None, alias="avatar_url")
    is_admin: bool = Field(default=False, alias="is_admin")

    model_config = ConfigDict(populate_by_name=True)


class UserCreate(UserBase):
    password_hash: str = Field(..., min_length=32, description="Pre-hashed password")


class UserPublic(UserBase):
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class UserListResponse(BaseModel):
    items: list[UserPublic]
    total: int