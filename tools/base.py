"""
Базовий контракт для tools (function calling).

Кожен tool має: name, description, schema (JSON Schema), handler(**kwargs).
Реєстр зберігає саме це — єдиний формат для всіх tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    """Контракт одного tool."""

    name: str
    description: str
    schema: dict[str, Any]  # JSON Schema для parameters
    handler: Callable[..., str]  # handler(**kwargs) -> str
