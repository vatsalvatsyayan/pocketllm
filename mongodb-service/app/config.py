from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field("pocketLLM MongoDB Service", env="APP_NAME")
    app_version: str = Field("0.1.0", env="APP_VERSION")
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    port: int = Field(8100, env="PORT")

    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db: str = Field("pocketllm", env="MONGODB_DB")
    users_collection: str = Field("users", env="MONGODB_USERS_COLLECTION")
    sessions_collection: str = Field("sessions", env="MONGODB_SESSIONS_COLLECTION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

