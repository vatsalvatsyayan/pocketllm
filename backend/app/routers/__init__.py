from fastapi import APIRouter

from app.routers import (
    auth,
    chat,
    session,
    users,
)

# TEMPORARY
router = APIRouter()
router.include_router(session.router, prefix="/sessions", tags=["session"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
