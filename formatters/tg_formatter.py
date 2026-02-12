"""
Форматування тексту для Telegram.

Обрано MarkdownV2 — суворіший, але єдиний варіант з чітким escaping.
Чому не HTML: MarkdownV2 типовий для AI (моделі повертають * _ `).
"""

from __future__ import annotations

import re
from typing import Optional

# MarkdownV2: повний набір спецсимволів (включно з . та ! — їх часто пропускають)
# https://core.telegram.org/bots/api#markdownv2-style
_MD2_ESCAPE = re.compile(r"([_*\[\]\(\)~`>#+\-=|{}.!\\])")


def escape_markdown_v2(text: str) -> str:
    """
    Екранує спецсимволи Telegram MarkdownV2.

    Чому потрібно: інакше _ * ` тощо Telegram сприймає як розмітку.
    Некоректна розмітка → TelegramBadRequest при send_message.
    """
    return _MD2_ESCAPE.sub(r"\\\1", text)


def format_for_telegram(text: str, *, allow_markdown: bool = False) -> tuple[str, Optional[str]]:
    """
    Готує текст для відправки в Telegram.

    Повертає (text, parse_mode). parse_mode="MarkdownV2" — пробуємо.
    Fallback при помилці — у handler при TelegramBadRequest (відправка без parse_mode).
    Args:
        text: сирий текст від AI
        allow_markdown: якщо True — довіряємо що текст уже валідний MarkdownV2;
            якщо False — екрануємо весь текст, щоб Telegram не відхилив розмітку.
    Returns:
        (відформатований текст, "MarkdownV2" або None для plain)
    """
    if not text or not text.strip():
        return "", None

    clean = text.strip()
    if not allow_markdown:
        clean = escape_markdown_v2(clean)

    return clean, "MarkdownV2"
