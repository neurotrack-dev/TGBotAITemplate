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

    # Для logger/telegram — обов'язково, якщо log_to_telegram=True
    TELEGRAM_BOT_FOR_REPORTS_KEY: Optional[str] = None
    TELEGRAM_GROUP_ID_FOR_LOGGER: Optional[str] = None


settings = Settings()

# Експорт для logger.telegram (from config import ...)
TELEGRAM_BOT_FOR_REPORTS_KEY = settings.TELEGRAM_BOT_FOR_REPORTS_KEY
TELEGRAM_GROUP_ID_FOR_LOGGER = settings.TELEGRAM_GROUP_ID_FOR_LOGGER
