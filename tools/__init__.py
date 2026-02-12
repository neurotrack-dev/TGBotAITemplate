"""
Tools — function calling для AI (наприклад OpenAI tools).

Чому тут нема імпортів tools:
- явна ініціалізація читабельніша для новачків (без “магії” імпорту)
- реєстрацію робимо через `tools.registry.register_all_tools()` у `main.py`
"""

from __future__ import annotations
