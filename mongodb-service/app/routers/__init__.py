from fastapi import APIRouter

from app.routers import sessions, users

router = APIRouter()
router.include_router(users.router)
router.include_router(sessions.router)

