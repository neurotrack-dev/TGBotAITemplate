"""
Обробник команди /start та головного меню.

Чому окремий файл: start — це окремий flow, його логіка не переплітається з chat.
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from logger import get_logger
from handlers.states import ChatState

logger = get_logger(__name__)

router = Router()


# Клавіатура з кнопками режимів
# Чому InlineKeyboard: не займає місце під полем вводу, виглядає акуратно
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Повертає головне меню з кнопкою Chat mode."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Chat mode", callback_data="chat_mode")],
    ])


def get_chat_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню в режимі чату — вихід назад до головного меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Exit chat", callback_data="exit_chat")],
    ])


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обробка /start — привітання, скидання стану і показ меню."""
    await state.clear()
    logger.info("Користувач %s натиснув /start", message.from_user.id)
    await message.answer(
        "Вітаю! Обери режим нижче.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "chat_mode")
async def cb_chat_mode(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обробка кнопки 'Chat mode' — встановлюємо FSM state.

    Чому callback_query: Inline-кнопки в aiogram використовують callback_data,
    обробляються через callback_query, не message.
    """
    await state.set_state(ChatState.active)
    await callback_query.answer()
    await callback_query.message.answer(
        "Режим чату активовано. Напиши будь-що — отримаєш відповідь від AI.",
        reply_markup=get_chat_menu_keyboard(),
    )


@router.callback_query(F.data == "exit_chat")
async def cb_exit_chat(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Вихід з режиму чату — state.clear() і повернення до меню."""
    await state.clear()
    await callback_query.answer()
    await callback_query.message.answer(
        "Вітаю! Обери режим нижче.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    """Команда /menu — вихід з чату і показ меню. /start теж скидає state (cmd_start)."""
    await state.clear()
    await message.answer(
        "Вітаю! Обери режим нижче.",
        reply_markup=get_main_menu_keyboard(),
    )
