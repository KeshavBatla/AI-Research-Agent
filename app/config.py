import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Model settings
    MODEL_NAME: str = "gemini-2.5-flash"

    # Server settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Research settings
    DEFAULT_MAX_ANALYSTS: int = 3
    DEFAULT_MAX_TURNS: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    """Return settings instance."""
    return Settings()
