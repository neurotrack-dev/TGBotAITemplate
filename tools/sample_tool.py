"""
Приклад tool для AI function calling.

Єдиний контракт: name, description, schema, handler(**kwargs).
"""

from __future__ import annotations

from datetime import datetime

from tools.base import Tool
from tools.registry import register_tool

# JSON Schema для parameters (порожній — tool не приймає аргументів)
SCHEMA = {"type": "object", "properties": {}, "required": []}


def handler() -> str:
    """Виконує tool. Викликається коли модель обирає get_current_time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tool = Tool(
    name="get_current_time",
    description="Повертає поточний час. Використовуй коли користувач питає про час або дату.",
    schema=SCHEMA,
    handler=handler,
)
register_tool(tool)


# Шаблон другого tool
# def handler_2() -> str:
#     return "результат"
# tool_2 = Tool(name="example_tool_2", description="Опис", schema={"type": "object", "properties": {}, "required": []}, handler=handler_2)
# register_tool(tool_2)
