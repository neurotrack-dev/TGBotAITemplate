"""
Обробник команди /start.

Чому окремий файл: start — окремий flow, логіка не переплітається з chat.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from db import UnitOfWork
from logger import logger
from services.chat_service import ChatService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обробка /start — User/Conversation у БД, привітання без клавіатури."""
    await logger.log(
        level="INFO",
        module=__name__,
        message=f"Користувач {message.from_user.id} натиснув /start",
    )
    async with UnitOfWork() as uow:
        chat_service = ChatService(uow.session)
        await chat_service.ensure_user_and_conversation(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
    await message.answer("Вас вітає AI-помічник по проекту. Пишіть будь-яке питання — відповім.")
