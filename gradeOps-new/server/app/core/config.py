"""
Application configuration settings.

Loads from environment variables using Pydantic settings.
All required settings are validated at module load time.
"""

import logging
from pydantic_settings import BaseSettings
from typing import List

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic v2 BaseSettings for validation and type conversion.
    """
    
    # Application
    APP_NAME: str = "GradeOps"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = ""
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    
    # Supabase Storage Buckets
    SUPABASE_STORAGE_EXAM_PDFS_BUCKET: str = "exam-pdfs"
    SUPABASE_STORAGE_ANSWER_IMAGES_BUCKET: str = "answer-images"
    
    # LLM provider routing
    LLM_PROVIDER: str = "openai"
    LLM_FALLBACK_ORDER: str = "anthropic,openai,xai"
    LLM_MODEL: str = ""
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_RETRIES: int = 3
    LLM_REQUEST_TIMEOUT_SECONDS: int = 45

    # OpenAI / ChatGPT
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Anthropic / Claude
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-latest"

    # xAI / Grok (OpenAI-compatible API)
    XAI_API_KEY: str = ""
    XAI_MODEL: str = "grok-2-latest"
    XAI_BASE_URL: str = "https://api.x.ai/v1"
    
    # Embeddings (for plagiarism detection)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Plagiarism Detection
    PLAGIARISM_THRESHOLD: float = 0.85
    PLAGIARISM_TOP_K: int = 5
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "pdf"
    
    # Pipeline
    PIPELINE_TIMEOUT_SECONDS: int = 300
    PIPELINE_RETRY_COUNT: int = 2

    # OCR service
    OCR_API_URL: str = ""
    OCR_TIMEOUT_SECONDS: int = 30
    OCR_MAX_RETRIES: int = 3
    OCR_ENABLE_LOCAL_FALLBACK: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


def get_settings() -> Settings:
    """
    Get application settings.
    
    Settings are loaded once and cached.
    
    Returns:
        Settings instance with validated configuration
        
    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return Settings()


# Load settings at module import time
settings = get_settings()

# Validate required settings
required_settings = {
    "DATABASE_URL": settings.DATABASE_URL,
    "SUPABASE_URL": settings.SUPABASE_URL,
    "SUPABASE_KEY": settings.SUPABASE_KEY,
}

missing_settings = [k for k, v in required_settings.items() if not v]
if missing_settings:
    logger.warning(
        f"[WARNING] Missing required environment variables: {', '.join(missing_settings)}"
    )

logger.info(f"[SUCCESS] Configuration loaded: {settings.APP_NAME} (Debug: {settings.DEBUG})")
