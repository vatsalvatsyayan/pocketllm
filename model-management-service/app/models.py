"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    """Single message in a conversation."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "What is Python?",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None


class InferenceRequest(BaseModel):
    """Request for LLM inference."""
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "session_id": "abc-123",
                "prompt": "What is Python?",
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
    )
    
    session_id: str = Field(..., description="Unique session identifier")
    prompt: str = Field(..., min_length=1, description="User prompt")
    stream: bool = Field(default=True, description="Whether to stream the response")
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="model_settings",
        description="Model-specific configuration (temperature, max_tokens, etc.)"
    )
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)


class InferenceResponse(BaseModel):
    """Response from LLM inference."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "abc-123",
                "response": "Python is a programming language...",
                "tokens_generated": 50,
                "tokens_prompt": 10,
                "cache_hit": False,
                "latency_ms": 1234.5,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    session_id: str
    response: str
    tokens_generated: int
    tokens_prompt: int
    cache_hit: bool = False
    cache_type: Optional[str] = None  # "l1" or "l2"
    latency_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CacheEntry(BaseModel):
    """Cache entry model."""
    hash: str
    response: str
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ttl: int


class StreamTokenEvent(BaseModel):
    """WebSocket event for streaming tokens."""
    event: str = "stream_token"
    data: Dict[str, Any]


class StreamCompleteEvent(BaseModel):
    """WebSocket event for completion."""
    event: str = "stream_complete"
    data: Dict[str, Any]


class StreamErrorEvent(BaseModel):
    """WebSocket event for errors."""
    event: str = "stream_error"
    data: Dict[str, Any]


class WebSocketMessage(BaseModel):
    """WebSocket message wrapper."""
    event: str
    data: Dict[str, Any]

