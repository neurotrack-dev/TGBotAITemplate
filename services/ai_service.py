"""
AI-сервіс для генерації відповідей.

Якщо OPENAI_API_KEY немає → mock. Якщо є → (пізніше) справжній виклик.
"""

from __future__ import annotations

from typing import Any, Optional

from config import settings
from logger import get_logger

logger = get_logger(__name__)

# Системний промпт англійською — так простіше переносити між різними LLM API.
SYSTEM_PROMPT = """You are an AI assistant inside a Telegram bot (internal architecture template).

Scope:
- Help users by answering their questions and/or explaining how this template works.
- If the request is unrelated to the bot/template scope, politely refuse and suggest what you *can* help with.

Quality rules:
- Be concise and structured (max 2–3 short paragraphs; bullet list if needed).
- No filler greetings. Start with the answer.
- If you are unsure, say so and ask 1 clarifying question.
- Do not invent facts, credentials, or external system state.
"""


def _build_messages(user_message: str) -> list[dict[str, str]]:
    """Збирає список повідомлень для API. Шар 1: збір промпту."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def _call_llm(messages: list[dict[str, str]], tools: Optional[list[dict[str, Any]]]) -> str:
    """
    Шар 2: виклик LLM.

    Якщо OPENAI_API_KEY є — виклик API. Інакше mock.
    """
    if not settings.OPENAI_API_KEY:
        logger.debug("OPENAI_API_KEY is not set, using mock reply")
    _ = tools
    # TODO: якщо settings.OPENAI_API_KEY — викликати openai.chat.completions.create(...)
    return (
        "(mock)\n"
        f"You said: {messages[-1]['content'][:200]}\n\n"
        "To enable real AI replies, set OPENAI_API_KEY and implement the OpenAI call."
    )


def generate_reply(user_message: str, tools: Optional[list[dict[str, Any]]] = None) -> str:
    """
    Генерує відповідь на повідомлення користувача.

    Args:
        user_message: текст від користувача
        tools: список tools для function calling (опціонально)

    Returns:
        Згенерована відповідь
    """
    logger.debug("Генерація відповіді для: %s...", user_message[:50])
    messages = _build_messages(user_message)
    return _call_llm(messages, tools)
