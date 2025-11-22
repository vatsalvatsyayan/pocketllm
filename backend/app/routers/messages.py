from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import database_dependency
from app.middleware.auth import get_current_user_id
from app.repositories.messages import MessageRepository
from app.repositories.sessions import SessionRepository
from app.schemas.messages import MessageCreate, MessageRead

router = APIRouter(
    prefix="/sessions/{session_id}/messages",
    tags=["messages"],
)


@router.get("", response_model=List[dict])
async def list_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    messages_repo = MessageRepository(database)
    sessions_repo = SessionRepository(database)

    # Ensure session belongs to this user
    session = await sessions_repo.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return await messages_repo.list_messages(
        session_id=session_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_message(
    session_id: str,
    payload: MessageCreate,
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    messages_repo = MessageRepository(database)
    sessions_repo = SessionRepository(database)

    # Ensure session belongs to this user
    session = await sessions_repo.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return await messages_repo.create_message(
        session_id=session_id,
        user_id=user_id,
        payload=payload,
    )
