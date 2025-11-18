from fastapi import APIRouter

from app.routers import (
    auth,
    chat,
    messages,
    session,
    users,
)


router = APIRouter()
router.include_router(session.router)
router.include_router(chat.router)
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(messages.router)
