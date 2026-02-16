"""
Обробник команди /start.

Чому окремий файл: start — окремий flow, логіка не переплітається з chat.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обробка /start — привітання без клавіатури."""
    await logger.log(
        level="INFO",
        module=__name__,
        message=f"Користувач {message.from_user.id} натиснув /start",
    )
    await message.answer("Вас вітає AI-помічник по проекту. Пишіть будь-яке питання — відповім.")
