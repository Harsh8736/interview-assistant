from pydantic_settings import BaseSettings
from typing import List





class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Interview Platform"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Gemini
    GROQ_API_KEY: str

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()