from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import database_dependency
from app.repositories.sessions import SessionRepository
from app.schemas.sessions import (
    ChatSessionCreate,
    ChatSessionPublic,
    ChatSessionUpdate,
)

router = APIRouter(prefix="/chat/sessions", tags=["Sessions"])


@router.post("/", response_model=ChatSessionPublic, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatSessionCreate, database: AsyncIOMotorDatabase = Depends(database_dependency)
):
    repository = SessionRepository(database)
    return await repository.create_session(payload)


@router.get("/{session_id}", response_model=ChatSessionPublic)
async def get_session(
    session_id: str, database: AsyncIOMotorDatabase = Depends(database_dependency)
):
    repository = SessionRepository(database)
    document = await repository.get_session(session_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return document


@router.patch("/{session_id}", response_model=ChatSessionPublic)
async def update_session(
    session_id: str,
    payload: ChatSessionUpdate,
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = SessionRepository(database)
    document = await repository.update_session(session_id, payload)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return document


@router.get(
    "/users/{user_id}",
    response_model=list[ChatSessionPublic],
    summary="List sessions for a user",
)
async def list_sessions_for_user(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = SessionRepository(database)
    return await repository.list_for_user(user_id=user_id, skip=skip, limit=limit)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str, database: AsyncIOMotorDatabase = Depends(database_dependency)
):
    repository = SessionRepository(database)
    success = await repository.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
