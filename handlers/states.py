"""
FSM-стани бота.

Чому FSM, а не in-memory set: FSM — еталонний підхід aiogram для flow.
Показує явний стан діалогу, легко розширити (наприклад додати choosing_topic).
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class ChatState(StatesGroup):
    """Стани режиму чату."""

    # Користувач натиснув "Chat mode" — бот реагує лише на повідомлення в цьому стані
    active = State()
