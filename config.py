"""
Конфігурація бота. Змінні з .env.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BOT_TOKEN: str
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Для logger/telegram — обов'язково, якщо log_to_telegram=True
    TELEGRAM_BOT_FOR_REPORTS_KEY: Optional[str] = None
    TELEGRAM_GROUP_ID_FOR_LOGGER: Optional[str] = None

    # PostgreSQL. Default підходить для Docker (user postgres). На macOS часто треба в .env свій user.
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/telegram_bot"
    # True = при старті викликати create_all() (схема з моделей). False = тільки перевірка підключення; схема — лише через Alembic.
    DB_CREATE_SCHEMA_ON_START: bool = False


settings = Settings()
