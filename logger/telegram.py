"""
Відправка повідомлень у Telegram через Bot API.
Використовується Logger'ом для доставки логів у чат/групу.
"""

from __future__ import annotations

import aiohttp
import asyncio
import logging

from config import TELEGRAM_BOT_FOR_REPORTS_KEY, TELEGRAM_GROUP_ID_FOR_LOGGER

_log = logging.getLogger("telegram_bot.remote_logger.telegram")


async def send_telegram_message(message: str):
    """
    Асинхронно відправити текст у Telegram.
    Args:
        message: Текст повідомлення для відправки.
    """
    token = TELEGRAM_BOT_FOR_REPORTS_KEY
    chat_id = TELEGRAM_GROUP_ID_FOR_LOGGER
    if not token or not chat_id:
        # Безпечна поведінка навіть якщо log_to_telegram=True, але env не задані
        _log.info("Telegram logging disabled (missing token/chat_id)")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                await response.json()
        except aiohttp.ClientError as e:
            _log.warning("Помилка відправки лога в Telegram: %s", e, exc_info=True)


# ------------------------------------------------------------------------------
# Тест: python -m logger.telegram
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(send_telegram_message("test"))
