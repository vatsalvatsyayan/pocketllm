from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import database_dependency
from app.middleware.auth import get_current_admin_user
from app.repositories.messages import MessageRepository
from app.repositories.sessions import SessionRepository
from app.repositories.users import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics")
async def get_metrics(
    user_id: str = Depends(get_current_admin_user),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """Get system-wide metrics for admin dashboard."""
    user_repo = UserRepository(database)
    session_repo = SessionRepository(database)
    message_repo = MessageRepository(database)
    
    # Total counts
    total_users = await user_repo.collection.count_documents({})
    total_sessions = await session_repo.collection.count_documents({})
    total_messages = await message_repo.collection.count_documents({})
    
    # Admin count
    admin_count = await user_repo.collection.count_documents({"is_admin": True})
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_users = await user_repo.collection.count_documents({
        "created_at": {"$gte": yesterday}
    })
    recent_sessions = await session_repo.collection.count_documents({
        "created_at": {"$gte": yesterday}
    })
    recent_messages = await message_repo.collection.count_documents({
        "created_at": {"$gte": yesterday}
    })
    
    # Messages by role
    user_messages = await message_repo.collection.count_documents({"role": "user"})
    assistant_messages = await message_repo.collection.count_documents({"role": "assistant"})
    
    # Active users (users with sessions in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_user_ids = await session_repo.collection.distinct(
        "user_id",
        {"updated_at": {"$gte": week_ago}}
    )
    active_users_count = len(active_user_ids)
    
    # Average messages per session
    avg_messages_per_session = (
        total_messages / total_sessions if total_sessions > 0 else 0
    )
    
    return {
        "overview": {
            "total_users": total_users,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "admin_count": admin_count,
            "active_users": active_users_count,
        },
        "recent_activity": {
            "new_users_24h": recent_users,
            "new_sessions_24h": recent_sessions,
            "new_messages_24h": recent_messages,
        },
        "messages": {
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "avg_per_session": round(avg_messages_per_session, 2),
        },
    }


@router.get("/users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_admin_user),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """List all users (admin only)."""
    user_repo = UserRepository(database)
    users, total = await user_repo.list_users(skip=skip, limit=limit)
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/sessions")
async def list_all_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_admin_user),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """List all sessions (admin only)."""
    session_repo = SessionRepository(database)
    sessions = await session_repo.collection.find({}).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
    total = await session_repo.collection.count_documents({})
    
    # Convert to public format
    from app.repositories.sessions import _public_session
    public_sessions = [_public_session(session) for session in sessions]
    
    return {
        "sessions": public_sessions,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/messages")
async def list_all_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_admin_user),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """List all messages (admin only)."""
    message_repo = MessageRepository(database)
    messages = await message_repo.collection.find({}).skip(skip).limit(limit).sort("created_at", -1).to_list(length=limit)
    total = await message_repo.collection.count_documents({})
    
    # Convert to public format
    from app.repositories.messages import _public_message
    public_messages = [_public_message(msg) for msg in messages]
    
    return {
        "messages": public_messages,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: str,
    user_admin_id: str = Depends(get_current_admin_user),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """Toggle admin status for a user."""
    user_repo = UserRepository(database)
    user = await user_repo.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-demotion
    if user_id == user_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin status",
        )
    
    new_admin_status = not user.get("is_admin", False)
    updated_user = await user_repo.update_user_admin_status(user_id, new_admin_status)
    
    return {
        "user": updated_user,
        "is_admin": new_admin_status,
    }

