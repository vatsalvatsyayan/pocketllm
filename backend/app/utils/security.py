from __future__ import annotations

import bcrypt

MAX_BCRYPT_INPUT_BYTES = 72


def _normalize_password(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) > MAX_BCRYPT_INPUT_BYTES:
        return encoded[:MAX_BCRYPT_INPUT_BYTES]
    return encoded


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    password_bytes = _normalize_password(password)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    password_bytes = _normalize_password(password)
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))