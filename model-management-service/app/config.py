"""Configuration management for Model Management Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 50
    
    # PostgreSQL Configuration
    DATABASE_URL: str = ""  # Empty = use placeholder mode
    
    # Model Server Configuration (Ollama)
    MODEL_SERVER_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "tinyllama"  # Default Ollama model name
    MODEL_SERVER_TIMEOUT: int = 30
    MODEL_MAX_RETRIES: int = 2
    MODEL_RETRY_DELAY: float = 2.0
    
    # Cache Configuration
    L1_CACHE_TTL: int = 86400  # 24 hours
    L2_CACHE_TTL: int = 604800  # 7 days
    CACHE_SIMILARITY_THRESHOLD: float = 0.85
    SESSION_CACHE_TTL: int = 1800  # 30 minutes
    
    # Queue Configuration
    MAX_QUEUE_SIZE: int = 50
    QUEUE_POLL_INTERVAL: float = 0.5
    
    # Rate Limiting Configuration
    MAX_REQUESTS_PER_HOUR: int = 100
    
    # JWT Configuration
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_PREFIX: str = "Bearer"
    
    # Context Configuration
    MAX_CONTEXT_TOKENS: int = 4096
    CONTEXT_TRUNCATION_MODE: str = "sliding_window"  # sliding_window or last_n
    MAX_HISTORY_MESSAGES: int = 50  # Maximum number of messages to load from history
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Application Configuration
    APP_NAME: str = "Model Management Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

