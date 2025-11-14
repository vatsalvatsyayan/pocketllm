"""JWT authentication middleware."""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt
import structlog

from app.config import settings

logger = structlog.get_logger()
security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens."""
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {"/health", "/", "/docs", "/openapi.json", "/redoc"}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate JWT token."""
        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Skip auth for WebSocket connections (handled separately)
        if request.url.path.startswith("/ws"):
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            logger.warning("Missing authorization header", path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract Bearer token
        if not authorization.startswith(settings.JWT_TOKEN_PREFIX):
            logger.warning("Invalid authorization format", path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization[len(settings.JWT_TOKEN_PREFIX) + 1:].strip()
        
        # Validate token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            # Attach user info to request state
            request.state.user_id = payload.get("sub") or payload.get("user_id")
            request.state.user_email = payload.get("email")
            
            logger.debug("Token validated", user_id=request.state.user_id)
            
        except JWTError as e:
            logger.warning("Token validation failed", error=str(e), path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return await call_next(request)

