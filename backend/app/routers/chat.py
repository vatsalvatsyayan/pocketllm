import json
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import database_dependency
from app.middleware.auth import get_current_user_id
from app.repositories.messages import MessageRepository
from app.repositories.sessions import SessionRepository
from app.schemas.messages import MessageCreate, ChatStreamRequest, ChatMessageRequest
from app.schemas.sessions import (
    ChatSessionCreate,
    ChatSessionCreateRequest,
    ChatSessionListResponse,
    ChatSessionPublic,
)
from app.services.model_client import stream_model_chat, ask_model_management

router = APIRouter(prefix="/chat", tags=["Chat"])


_SORT_FIELD_MAPPING = {
    "createdAt": "created_at",
    "updatedAt": "updated_at",
    "title": "title",
}


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("updatedAt", regex="^(createdAt|updatedAt|title)$"),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = SessionRepository(database)
    skip = (page - 1) * limit
    sort_field = _SORT_FIELD_MAPPING.get(sort_by, "updated_at")
    sort_direction = -1 if sort_order == "desc" else 1

    sessions = await repository.list_for_user(
        user_id=user_id,
        limit=limit,
        skip=skip,
        sort_field=sort_field,
        sort_direction=sort_direction,
    )
    total = await repository.count_for_user(user_id)
    has_more = skip + len(sessions) < total

    return ChatSessionListResponse(
        data=[ChatSessionPublic(**session) for session in sessions],
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.post(
    "/sessions",
    response_model=ChatSessionPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    payload: ChatSessionCreateRequest,
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = SessionRepository(database)
    session = await repository.create_session(
        ChatSessionCreate(
            user_id=user_id,
            title=payload.title,
            metadata=payload.metadata,
        )
    )
    return ChatSessionPublic(**session)


@router.get(
    "/sessions/{session_id}",
    response_model=ChatSessionPublic,
)
async def get_session_detail(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    repository = SessionRepository(database)
    session = await repository.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return ChatSessionPublic(**session)


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """Get messages for a specific chat session."""
    messages_repo = MessageRepository(database)
    sessions_repo = SessionRepository(database)

    # Ensure session belongs to this user
    session = await sessions_repo.get_session(session_id, user_id=user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    messages = await messages_repo.list_messages(
        session_id=session_id,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    
    # Return format expected by frontend
    return {
        "sessionId": session_id,
        "messages": messages,
        "total": len(messages),  # Note: This is approximate, could add count query if needed
    }


@router.post("/stream")
async def stream_chat(
    payload: ChatStreamRequest,
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    session_id = payload.session_id
    
    # 1. Validate Session
    session_repo = SessionRepository(database)
    session = await session_repo.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save User Message
    message_repo = MessageRepository(database)
    await message_repo.create_message(
        session_id,
        user_id,
        MessageCreate(role="user", content=payload.prompt)
    )

    # 2.5. Load message history to pass to model-management-service
    messages = await message_repo.list_messages(
        session_id=session_id,
        user_id=user_id,
        limit=50,  # Match MAX_HISTORY_MESSAGES
        offset=0,
    )
    # Format messages for model-management-service (only role and content)
    message_history = [
        {"role": msg.get("role"), "content": msg.get("content")}
        for msg in messages
    ]

    # 3. Prepare Model Request
    model_payload = {
        "session_id": session_id,
        "prompt": payload.prompt,
        "stream": True,
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": message_history,  # Pass message history for context
    }

    # 4. Stream and Accumulate
    async def response_generator():
        full_response_text = ""
        try:
            async for line in stream_model_chat("/inference/chat/stream", model_payload):
                # line is a string like "data: {...}"
                if line.strip():
                    # Parse for accumulation and transformation
                    if line.startswith("data: "):
                        try:
                            data_str = line.replace("data: ", "").strip()
                            if data_str == "[DONE]": 
                                continue
                            
                            data = json.loads(data_str)
                            
                            # Handle error from model service
                            if data.get("error"):
                                yield f"data: {json.dumps({'type': 'error', 'error': data['error']})}\n\n"
                                return

                            token = data.get("token", "")
                            done = data.get("done", False)
                            
                            if token:
                                full_response_text += token
                                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                            
                            if done:
                                yield f"data: {json.dumps({'type': 'end', 'messageId': payload.message_id})}\n\n"
                                
                        except Exception:
                            pass
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            return

        # 5. Save Assistant Message (after stream ends)
        if full_response_text:
             await message_repo.create_message(
                session_id,
                user_id,
                MessageCreate(role="assistant", content=full_response_text)
            )

    return StreamingResponse(response_generator(), media_type="text/event-stream")


@router.post("/message")
async def send_message(
    payload: ChatMessageRequest,
    user_id: str = Depends(get_current_user_id),
    database: AsyncIOMotorDatabase = Depends(database_dependency),
):
    """Non-streaming chat endpoint."""
    session_id = payload.session_id
    
    # 1. Validate Session
    session_repo = SessionRepository(database)
    session = await session_repo.get_session(session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save User Message
    message_repo = MessageRepository(database)
    await message_repo.create_message(
        session_id,
        user_id,
        MessageCreate(role="user", content=payload.prompt)
    )

    # 2.5. Load message history to pass to model-management-service
    messages = await message_repo.list_messages(
        session_id=session_id,
        user_id=user_id,
        limit=50,  # Match MAX_HISTORY_MESSAGES
        offset=0,
    )
    # Format messages for model-management-service (only role and content)
    message_history = [
        {"role": msg.get("role"), "content": msg.get("content")}
        for msg in messages
    ]

    # 3. Prepare Model Request
    model_payload = {
        "session_id": session_id,
        "prompt": payload.prompt,
        "stream": False,
        "temperature": payload.temperature,
        "messages": message_history,  # Pass message history for context
    }
    if payload.max_tokens:
        model_payload["max_tokens"] = payload.max_tokens

    # 4. Call Model Management Service
    try:
        response = await ask_model_management("/inference/chat", model_payload)
        
        # Extract response text
        response_text = response.get("response", "")
        if not response_text:
            raise HTTPException(
                status_code=500,
                detail="Empty response from model service"
            )
        
        # 5. Save Assistant Message
        await message_repo.create_message(
            session_id,
            user_id,
            MessageCreate(role="assistant", content=response_text)
        )
        
        return {
            "messageId": f"msg-{datetime.now().timestamp()}",
            "sessionId": session_id,
            "content": response_text,
            "role": "assistant",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get response from model: {str(e)}"
        )
