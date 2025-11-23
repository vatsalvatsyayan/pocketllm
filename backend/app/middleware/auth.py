from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings
from app.db import database_dependency

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ACCESS_TOKEN_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 60


@dataclass
class AuthPayload:
    sub: str
    scopes: List[str]
    exp: datetime


class JWTAuthenticator:
    def __init__(self, secret: str, algorithm: str = ALGORITHM):
        self.secret = secret
        self.algorithm = algorithm

    def create_access_token(self, subject: str, scopes: List[str] | None = None) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload: Dict[str, Any] = {
            "sub": subject,
            "scopes": scopes or [],
            "exp": expire,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> AuthPayload:
        try:
            decoded = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            exp_ts = decoded.get("exp")
            if exp_ts is None:
                raise ValueError("Token missing expiration")
            return AuthPayload(
                sub=decoded.get("sub"),
                scopes=decoded.get("scopes", []),
                exp=datetime.utcfromtimestamp(int(exp_ts)),
            )
        except JWTError as exc:
            raise ValueError("Invalid or expired token") from exc


authenticator = JWTAuthenticator(settings.jwt_secret)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_authenticator() -> JWTAuthenticator:
    return authenticator


def decode_access_token(token: str = Depends(oauth2_scheme)) -> AuthPayload:
    try:
        return authenticator.decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(payload: AuthPayload = Depends(decode_access_token)) -> AuthPayload:
    if not payload.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_user_id(payload: AuthPayload = Depends(get_current_user)) -> str:
    return payload.sub


async def get_current_admin_user(
    user_id: str = Depends(get_current_user_id),
    database = Depends(database_dependency),
) -> str:
    """Verify that the current user is an admin."""
    from app.repositories.users import UserRepository
    
    user_repo = UserRepository(database)
    user = await user_repo.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return user_id
