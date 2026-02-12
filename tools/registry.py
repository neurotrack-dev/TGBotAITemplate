"""
Реєстр tools для AI function calling.

Зберігає tools у єдиному контракті: name, description, schema, handler.
"""

from __future__ import annotations

from typing import Any, Optional

from tools.base import Tool

TOOLS: list[Tool] = []
_TOOLS_REGISTERED: bool = False


def register_all_tools() -> None:
    """
    Явно реєструє всі tools.

    Чому так зроблено: щоб уникнути прихованого глобального стану “через імпорт”.
    Новачок додає новий tool у `tools/`, а потім підключає його тут.
    """
    global _TOOLS_REGISTERED
    if _TOOLS_REGISTERED:
        return

    # Імпорт модулів, які викликають register_tool(...) при імпорті
    # Додай новий tool: створити tools/my_tool.py і додати імпорт нижче
    from tools import sample_tool  # noqa: F401

    _TOOLS_REGISTERED = True


def register_tool(tool: Tool) -> None:
    """Реєструє tool."""
    TOOLS.append(tool)


def get_tools() -> list[dict[str, Any]]:
    """
    Повертає tools у форматі OpenAI API для chat.completions.create(tools=...).
    """
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.schema,
            },
        }
        for t in TOOLS
    ]


def get_tool_handler(name: str) -> Optional[Tool]:
    """Повертає tool за іменем (для виконання після вибору моделлю)."""
    for t in TOOLS:
        if t.name == name:
            return t
    return None
