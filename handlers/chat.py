"""
Обробник повідомлень у режимі чату.

Чому окремий файл: логіка чату (AI, форматування) відокремлена від start.
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from logger import logger
from services.ai_service import generate_reply
from formatters.tg_formatter import format_for_telegram
from handlers.states import ChatState
from tools.registry import get_tools

router = Router()


# Обробляємо текстові повідомлення лише в стані ChatState.active
@router.message(ChatState.active, F.text)
async def handle_chat_message(message: Message) -> None:
    """
    Flow: отримати повідомлення → AI → форматування → відправити.

    Fallback: ловимо TelegramBadRequest при send_message — тоді plain text.
    Чому саме тут: fallback працює лише коли ловимо помилку Telegram API, не в formatter.
    """
    user_text = message.text or ""
    if not user_text.strip():
        return

    await logger.log(
        level="INFO",
        module=__name__,
        message=f"Повідомлення від {message.from_user.id}: {user_text[:50]}...",
    )

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Генерація відповіді (tools передаємо для майбутнього OpenAI)
    raw_reply = await generate_reply(user_text, tools=get_tools())

    # Форматування під Telegram (MarkdownV2)
    formatted_reply, parse_mode = format_for_telegram(raw_reply)

    try:
        if parse_mode:
            await message.answer(formatted_reply, parse_mode=parse_mode)
        else:
            await message.answer(formatted_reply)
    except TelegramBadRequest as e:
        await logger.log(
            level="WARNING",
            module=__name__,
            message=f"MarkdownV2 відхилено Telegram, fallback на plain text: {e}",
        )
        # Лише повторна відправка без parse_mode. НЕ state.clear(), НЕ меню.
        await message.answer(raw_reply.strip())
