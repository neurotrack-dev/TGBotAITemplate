"""
Модуль логування для бота.

Експортує:
  - logger — асинхронний логер з відправкою в Telegram (для звітів)
  - get_logger(name) — стандартний sync-логер для handlers
"""

from __future__ import annotations

from logger.logger_module import Logger
from config import settings

# ------------------------------------------------------------------------------
# Telegram увімкнено лише якщо задані обидві змінні — інакше без падіння.
# ------------------------------------------------------------------------------
_log_to_telegram = bool(
    settings.TELEGRAM_BOT_FOR_REPORTS_KEY and settings.TELEGRAM_GROUP_ID_FOR_LOGGER
)
logger = Logger(log_to_telegram=_log_to_telegram)

# ------------------------------------------------------------------------------
# Інтеграція з handlers: get_logger повертає стандартний logging.Logger.
# ------------------------------------------------------------------------------
import logging
import sys

_std = logging.getLogger("telegram_bot")
_std.setLevel(logging.INFO)
if not _std.handlers:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    _std.addHandler(h)


def get_logger(name: str) -> logging.Logger:
    """Повертає логер для модуля. Використовуй: get_logger(__name__)."""
    prefix = "" if name.startswith("telegram_bot.") else "telegram_bot."
    return logging.getLogger(f"{prefix}{name}")
