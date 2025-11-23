from __future__ import annotations

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def _split_origins(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings(BaseSettings):
    app_name: str = Field("pocketLLM Backend", env="APP_NAME")
    app_version: str = Field("0.1.0", env="APP_VERSION")
    debug: bool = Field(True, env="DEBUG")
    allowed_origins: Optional[str] = Field(None, env="ALLOWED_ORIGINS")
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    model_management_url: str = Field("http://localhost:8000/api/v1", env="MODEL_MANAGEMENT_URL")
    jwt_secret: str = Field("replace-this-secret", env="JWT_SECRET")
    rate_limit_global: str = Field("100/minute", env="RATE_LIMIT_GLOBAL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db: str = Field("pocketllm", env="MONGODB_DB")
    users_collection: str = Field("users", env="MONGODB_USERS_COLLECTION")
    sessions_collection: str = Field("sessions", env="MONGODB_SESSIONS_COLLECTION")
    messages_collection: str = Field("messages", env="MONGODB_MESSAGES_COLLECTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
        populate_by_name = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allowed_origins = _split_origins(self.allowed_origins)


settings = Settings()
