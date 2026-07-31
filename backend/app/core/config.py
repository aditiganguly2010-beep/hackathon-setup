from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # LLM Configuration
    GOOGLE_ADK_API_KEY: str
    GOOGLE_ADK_PROJECT_ID: str
    LLM_MODEL: str = "gemini-pro"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # LangTrace
    LANGTRACE_API_KEY: Optional[str] = None
    LANGTRACE_HOST: str = "https://api.langtrace.ai"
    
    # Langfuse
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache
    CACHE_TTL_SECONDS: int = 300
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
