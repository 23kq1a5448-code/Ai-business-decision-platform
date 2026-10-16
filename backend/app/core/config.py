from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./business_platform.db",
        description="Database connection URL"
    )

    # JWT
    JWT_SECRET_KEY: str = Field(
        ...,
        description="JWT secret key for token generation"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_UPLOAD_EXTENSIONS: str = ".csv,.xlsx"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    # Email (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    # Redis (Optional)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
