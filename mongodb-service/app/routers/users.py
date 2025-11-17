from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.db import database_dependency
from app.repositories.users import UserRepository
from app.schemas.users import UserCreate, UserListResponse, UserPublic

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate, database: AsyncIOMotorDatabase = Depends(database_dependency)
):
    repository = UserRepository(database)
    try:
        document = await repository.create_user(payload)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists.",
        )
    return document


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = UserRepository(database)
    items, total = await repository.list_users(skip=skip, limit=limit)
    return UserListResponse(items=items, total=total)


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, database: AsyncIOMotorDatabase = Depends(database_dependency)):
    repository = UserRepository(database)
    document = await repository.get_user(user_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return document

