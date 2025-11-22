from __future__ import annotations

from typing import Any, Mapping

from bson import ObjectId
from fastapi import HTTPException, status


def parse_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception as exc:  # pragma: no cover - simple validation helper
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid ObjectId: {value}",
        ) from exc


def to_public_id(document: Mapping[str, Any]) -> Mapping[str, Any]:
    doc = dict(document)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    doc.pop("password_hash", None)
    return doc