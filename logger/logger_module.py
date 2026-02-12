"""
Клас Logger — логування в консоль, файл і Telegram.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from logger.telegram import send_telegram_message

_log = logging.getLogger("telegram_bot.remote_logger")


class Logger:
    LEVEL_EMOJIS = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
        "DEBUG": "🐛",
    }

    def __init__(
        self,
        default_level="INFO",
        log_to_file=True,
        log_to_telegram=False,
        log_file="logs.txt",
    ):
        """
        Ініціалізація логера.
        Args:
            default_level: Рівень логування за замовчуванням.
            log_to_file: Чи записувати логи у файл.
            log_to_telegram: Чи відправляти логи в Telegram.
            log_file: Шлях до файлу логів.
        """
        self.default_level = default_level
        self.log_to_file = log_to_file
        self.log_to_telegram = log_to_telegram
        self.log_file = log_file

    async def log(self, level: str, message: str, module: str = "General"):
        """
        Записати лог. Викликай з await.
        Args:
            level: Рівень (INFO, WARNING, ERROR, CRITICAL, DEBUG).
            message: Текст повідомлення.
            module: Назва модуля/компонента для контексту.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = (level or self.default_level).upper()
        emoji = self.LEVEL_EMOJIS.get(level, "🔍")
        log_entry = f"{emoji} [{timestamp}] [{level}] [{module}] - {message}"

        # Консоль/лог-система — через стандартний logging (без print)
        if level == "DEBUG":
            _log.debug(log_entry)
        elif level == "WARNING":
            _log.warning(log_entry)
        elif level in ("ERROR", "CRITICAL"):
            _log.error(log_entry)
        else:
            _log.info(log_entry)

        # Файл — якщо ввімкнено (зручно для дебагу)
        if self.log_to_file:
            try:
                with open(self.log_file, "a") as file:
                    file.write(log_entry + "\n")
            except IOError as e:
                _log.exception("Помилка запису в файл логів: %s", e)

        # Telegram — для важливих подій (звіти, помилки)
        if self.log_to_telegram:
            await self._send_to_telegram(log_entry)

    async def _send_to_telegram(self, message: str):
        """Відправити лог у Telegram через Bot API."""
        await send_telegram_message(message)


# ------------------------------------------------------------------------------
# Тест: python -m logger.logger_module
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    from logger import logger

    asyncio.run(
        logger.log(level="ERROR", module="Рассылка отчетов", message="Тестовый лог")
    )
