from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


@dataclass
class AuthPayload:
    sub: str
    scopes: list[str]
    exp: datetime


class JWTAuthenticator:
    def __init__(self, secret: str, algorithm: str = ALGORITHM):
        self.secret = secret
        self.algorithm = algorithm

    def create_access_token(self, subject: str, scopes: list[str] | None = None) -> str:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload: dict[str, Any] = {
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
            raise ValueError("Invalid token") from exc


def get_authenticator() -> JWTAuthenticator:
    return JWTAuthenticator(settings.jwt_secret)
