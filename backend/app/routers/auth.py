from fastapi import APIRouter, Depends, HTTPException, status

from app.db import database_dependency
from app.middleware.auth import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    get_authenticator,
    get_current_user,
)
from app.repositories.users import UserRepository
from app.schemas.auth import (
    AuthLoginRequest,
    AuthResponse,
    AuthSignupRequest,
    UserMeResponse,
)
from app.schemas.users import UserCreate, UserPublic
from app.utils.security import hash_password, verify_password
from app.utils.serializers import to_public_id

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_auth_response(user: dict) -> AuthResponse:
    token = get_authenticator().create_access_token(user["id"])
    return AuthResponse(
        token=token,
        expiresIn=ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserPublic.model_validate(user),
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(payload: AuthSignupRequest, database=Depends(database_dependency)) -> AuthResponse:
    repository = UserRepository(database)

    existing_user = await repository.find_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    hashed_password = hash_password(payload.password)
    user = await repository.create_user(
        UserCreate(
            email=payload.email,
            name=payload.name,
            avatar=payload.avatar_url,
            password_hash=hashed_password,
        )
    )

    return _build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login(payload: AuthLoginRequest, database=Depends(database_dependency)) -> AuthResponse:
    repository = UserRepository(database)
    document = await repository.find_by_email_with_hash(payload.email)

    if not document or not verify_password(payload.password, document.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = to_public_id(document)
    return _build_auth_response(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    # Stateless logout (client simply drops the token)
    return None


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(payload=Depends(get_current_user), database=Depends(database_dependency)) -> AuthResponse:
    repository = UserRepository(database)
    user = await repository.get_user(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return _build_auth_response(user)


@router.get("/me", response_model=UserMeResponse)
async def current_user(payload=Depends(get_current_user), database=Depends(database_dependency)) -> UserMeResponse:
    repository = UserRepository(database)
    user = await repository.get_user(payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserMeResponse(user=UserPublic.model_validate(user))
