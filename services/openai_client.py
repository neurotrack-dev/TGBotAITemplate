"""
Клієнт OpenAI: імпорт AsyncOpenAI та створення клієнта.

Якщо бібліотека openai не встановлена — get_client повертає None, get_import_error() — текст помилки.
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from openai import AsyncOpenAI  # type: ignore[import-untyped]
    _openai_available = True
    _import_error: Optional[str] = None
except Exception as e:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore[misc, assignment]
    _openai_available = False
    _import_error = str(e)


def is_available() -> bool:
    """Чи вдалося імпортувати OpenAI SDK."""
    return _openai_available


def get_import_error() -> Optional[str]:
    """Повідомлення помилки імпорту, якщо SDK недоступний."""
    return _import_error


def get_client(api_key: str) -> Any:
    """
    Повертає AsyncOpenAI(api_key=api_key) або None, якщо SDK не встановлено.
    """
    if not _openai_available:
        return None
    return AsyncOpenAI(api_key=api_key)
