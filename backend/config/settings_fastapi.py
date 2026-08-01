"""
FastAPI Settings — Banking Management System
Uses Pydantic BaseSettings to load and validate all env variables.
This is the single source of truth for the FastAPI application config.

Usage:
    from config.settings_fastapi import settings
    print(settings.DATABASE_URL)
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All application settings loaded from environment variables (or .env file).
    Pydantic validates types automatically — missing required fields raise errors at startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",          # ignore extra env vars we don't need
    )

    # ------------------------------------------------------------------
    # App
    # ------------------------------------------------------------------
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    # ------------------------------------------------------------------
    # PostgreSQL
    # ------------------------------------------------------------------
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "banking_db"
    POSTGRES_USER: str = "banking_user"
    POSTGRES_PASSWORD: str = "banking_pass"
    DATABASE_URL: str = "postgresql+asyncpg://banking_user:banking_pass@db:5432/banking_db"

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://redis:6379/0"

    # ------------------------------------------------------------------
    # Celery
    # ------------------------------------------------------------------
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # ------------------------------------------------------------------
    # JWT Authentication
    # ------------------------------------------------------------------
    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    EMAIL_USE_TLS: bool = True
    DEFAULT_FROM_EMAIL: str = "BankingMS <no-reply@bankingms.com>"

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "logs/app.log"

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


# ------------------------------------------------------------------
# Singleton — import `settings` anywhere in the app
# ------------------------------------------------------------------
@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    lru_cache ensures .env is only read once (not on every import).
    """
    return Settings()


# Module-level singleton for easy import
settings = get_settings()
