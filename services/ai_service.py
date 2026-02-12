"""
AI-сервіс для генерації відповідей.

Якщо OPENAI_API_KEY немає → mock. Якщо є → (пізніше) справжній виклик.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Optional

from config import settings
from logger import logger
from tools.registry import get_tool_handler

@lru_cache(maxsize=1)
def _load_system_prompt() -> str:
    """
    Завантажує системний промпт з файлу.

    Чому окремий файл: так легше підтримувати промпт, робити ревʼю та версіонувати
    без правок у коді сервісу.
    """
    prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "system_prompt.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        # Безпечний fallback, щоб бот не падав якщо файл випадково видалили
        return "You are a helpful AI assistant in a Telegram bot. Be concise and honest."


def _build_messages(user_message: str) -> list[dict[str, str]]:
    """Збирає список повідомлень для API. Шар 1: збір промпту."""
    return [
        {"role": "system", "content": _load_system_prompt()},
        {"role": "user", "content": user_message},
    ]


async def _call_llm(messages: list[dict[str, str]], tools: Optional[list[dict[str, Any]]]) -> str:
    """
    Шар 2: виклик LLM.

    Якщо OPENAI_API_KEY є — виклик API. Інакше mock.
    """
    if not settings.OPENAI_API_KEY:
        await logger.log(level="DEBUG", module=__name__, message="Using mock reply (no OPENAI_API_KEY)")
        return (
            "(mock)\n"
            f"You said: {messages[-1]['content'][:200]}\n\n"
            "To enable real AI replies, set OPENAI_API_KEY and implement the OpenAI call."
        )

    # Реальний виклик OpenAI (async). Якщо бібліотека не встановлена — повертаємо mock з поясненням.
    try:
        from openai import AsyncOpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        await logger.log(level="ERROR", module=__name__, message=f"OpenAI SDK import failed: {e}")
        return "(error) OpenAI SDK is not installed. Install `openai` package."

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    tool_defs = tools if tools else None

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        tools=tool_defs,
    )

    msg = response.choices[0].message

    # Якщо модель викликає tools — виконуємо їх і робимо ще один запит
    tool_calls = getattr(msg, "tool_calls", None)
    if tool_calls:
        # Додаємо assistant message з tool_calls (формат OpenAI messages)
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tc in tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}

            tool = get_tool_handler(name)
            if not tool:
                result = f"Tool '{name}' is not registered."
            else:
                try:
                    result = tool.handler(**args)
                except Exception as e:  # pragma: no cover
                    result = f"Tool '{name}' failed: {e}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

        response2 = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=tool_defs,
        )
        return (response2.choices[0].message.content or "").strip()

    return (msg.content or "").strip()


async def generate_reply(user_message: str, tools: Optional[list[dict[str, Any]]] = None) -> str:
    """
    Генерує відповідь на повідомлення користувача.

    Args:
        user_message: текст від користувача
        tools: список tools для function calling (опціонально)

    Returns:
        Згенерована відповідь
    """
    await logger.log(
        level="DEBUG",
        module=__name__,
        message=f"Генерація відповіді для: {user_message[:50]}...",
    )
    messages = _build_messages(user_message)
    return await _call_llm(messages, tools)
