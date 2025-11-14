"""Session management service."""
from typing import List, Optional, Dict, Any
import json
import structlog
from datetime import datetime

from app.config import settings
from app.services.cache_manager import get_redis_client
from app.utils.token_counter import count_tokens_in_messages

logger = structlog.get_logger()


class SessionManager:
    """Manages user sessions and message history."""
    
    def __init__(self):
        """Initialize session manager."""
        pass
    
    async def load_session(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Load session messages from cache or database.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of messages in the session
        """
        redis_client = await get_redis_client()
        from app.services.cache_manager import PlaceholderRedis
        
        # Try Redis first (if available)
        if not isinstance(redis_client, PlaceholderRedis):
            cache_key = f"session:{session_id}"
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                try:
                    messages = json.loads(cached_data)
                    logger.debug("Session loaded from cache", session_id=session_id, message_count=len(messages))
                    return messages
                except json.JSONDecodeError:
                    logger.warning("Failed to parse cached session data", session_id=session_id)
        
        # Fallback to PostgreSQL (placeholder - implement actual DB query)
        # For now, return empty list
        logger.debug("Session not found in cache, checking database", session_id=session_id)
        messages = await self._load_from_database(session_id)
        
        # Cache the result if found and Redis is available
        if messages and not isinstance(redis_client, PlaceholderRedis):
            await self.cache_session(session_id, messages)
        
        return messages
    
    async def _load_from_database(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Load session from PostgreSQL database.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of messages
        """
        try:
            from app.services.database import get_db_session, PlaceholderSession
            from sqlalchemy import text
            
            async for session in get_db_session():
                # Check if using placeholder session
                if isinstance(session, PlaceholderSession):
                    logger.debug("Database unavailable, returning empty session", session_id=session_id)
                    return []
                
                # Query messages from database
                # Assumes table structure: messages(session_id, role, content, timestamp)
                result = await session.execute(
                    text("""
                        SELECT role, content, timestamp 
                        FROM messages 
                        WHERE session_id = :session_id 
                        ORDER BY timestamp ASC
                        LIMIT :limit
                    """),
                    {
                        "session_id": session_id,
                        "limit": settings.MAX_HISTORY_MESSAGES
                    }
                )
                
                messages = []
                for row in result:
                    messages.append({
                        "role": row[0],
                        "content": row[1],
                        "timestamp": row[2].isoformat() if row[2] else None
                    })
                
                logger.debug(
                    "Loaded session from database",
                    session_id=session_id,
                    message_count=len(messages)
                )
                return messages
        except Exception as e:
            logger.warning("Failed to load session from database", session_id=session_id, error=str(e))
            return []
    
    async def cache_session(self, session_id: str, messages: List[Dict[str, Any]]):
        """
        Cache session messages in Redis.
        
        Args:
            session_id: Unique session identifier
            messages: List of messages to cache
        """
        redis_client = await get_redis_client()
        from app.services.cache_manager import PlaceholderRedis
        
        # Check if using placeholder Redis
        if isinstance(redis_client, PlaceholderRedis):
            logger.debug("Redis unavailable, skipping session cache", session_id=session_id)
            return
        
        cache_key = f"session:{session_id}"
        
        try:
            messages_json = json.dumps(messages, default=str)
            await redis_client.setex(
                cache_key,
                settings.SESSION_CACHE_TTL,
                messages_json
            )
            logger.debug(
                "Session cached",
                session_id=session_id,
                message_count=len(messages),
                ttl=settings.SESSION_CACHE_TTL,
            )
        except Exception as e:
            logger.warning("Failed to cache session", session_id=session_id, error=str(e))
    
    async def save_message_to_database(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: Optional[str] = None,
    ):
        """
        Save a message to the PostgreSQL database.
        
        Args:
            session_id: Unique session identifier
            role: Message role (user/assistant/system)
            content: Message content
            user_id: Optional user identifier
        """
        try:
            from app.services.database import get_db_session, PlaceholderSession
            from sqlalchemy import text
            
            async for session in get_db_session():
                # Check if using placeholder session
                if isinstance(session, PlaceholderSession):
                    logger.debug("Database unavailable, skipping save", session_id=session_id)
                    return
                
                # Insert message into database
                # Assumes table structure: messages(session_id, user_id, role, content, timestamp)
                await session.execute(
                    text("""
                        INSERT INTO messages (session_id, user_id, role, content, timestamp) 
                        VALUES (:session_id, :user_id, :role, :content, NOW())
                    """),
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "role": role,
                        "content": content
                    }
                )
                await session.commit()
                logger.debug(
                    "Saved message to database",
                    session_id=session_id,
                    role=role,
                    content_length=len(content),
                )
                break
        except Exception as e:
            logger.warning("Failed to save message to database (using placeholder)", error=str(e))
    
    def count_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Count tokens in a list of messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Total token count
        """
        return count_tokens_in_messages(messages)

