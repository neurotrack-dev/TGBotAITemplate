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
from . import openai_client


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
        return (
            "You are a helpful AI assistant in a Telegram bot. Be concise and honest."
        )


def _ensure_system_message(messages: list[dict]) -> list[dict]:
    """Якщо немає system — додає на початок."""
    if messages and messages[0].get("role") == "system":
        return messages
    return [{"role": "system", "content": _load_system_prompt()}] + list(messages)


async def _call_llm(
    messages: list[dict[str, str]], tools: Optional[list[dict[str, Any]]]
) -> str:
    """
    Шар 2: виклик LLM.

    Якщо OPENAI_API_KEY є — виклик API. Інакше mock.
    """
    if not settings.OPENAI_API_KEY:
        await logger.log(
            level="DEBUG",
            module=__name__,
            message="Using mock reply (no OPENAI_API_KEY)",
        )
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), messages[-1])
        content = last_user.get("content", "")[:200] if isinstance(last_user.get("content"), str) else ""
        return (
            "(mock)\n"
            f"You said: {content}\n\n"
            "To enable real AI replies, set OPENAI_API_KEY and implement the OpenAI call."
        )

    client = openai_client.get_client(settings.OPENAI_API_KEY)
    if client is None:
        await logger.log(
            level="ERROR",
            module=__name__,
            message=f"OpenAI SDK import failed: {openai_client.get_import_error()}",
        )
        return "(error) OpenAI SDK is not installed. Install `openai` package."

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


async def generate_reply(
    messages: list[dict],
    tools: Optional[list[dict[str, Any]]] = None,
) -> str:
    """
    Генерує відповідь по історії повідомлень.

    Args:
        messages: список {"role": "user"|"assistant"|"system", "content": "..."}
        tools: список tools для function calling (опціонально)

    Returns:
        Згенерована відповідь
    """
    messages = _ensure_system_message(messages)
    return await _call_llm(messages, tools)
