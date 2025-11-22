from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.schemas.users import UserPublic


class AuthLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class AuthSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class AuthResponse(BaseModel):
    token: str
    expires_in: int = Field(..., alias="expiresIn")
    user: UserPublic

    class Config:
        populate_by_name = True


class UserMeResponse(BaseModel):
    user: UserPublic

    class Config:
        populate_by_name = True
