"""
Точка входу в Telegram-бота.

Чому так зроблено: main.py лише запускає бота, вся логіка в handlers та services.
Це дозволяє легко тестувати окремі модулі і тримати main мінімальним.
"""

from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from logger import logger
from handlers import start, chat
from tools.registry import register_all_tools


def register_routers(dp: Dispatcher) -> None:
    """Підключаємо всі роутери до Dispatcher."""
    dp.include_router(start.router)
    dp.include_router(chat.router)


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    # FSM потребує storage — MemoryStorage для in-memory (під Redis пізніше)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Явна реєстрація tools — без “магії” імпортів
    register_all_tools()

    register_routers(dp)

    await logger.log(level="INFO", module=__name__, message="Бот запущено")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
