"""
Форматування тексту для Telegram. Тільки HTML.

Код (block і inline) спочатку виноситься в плейсхолдери, потім escape + bold/italic,
потім код повертається. Жодного перетину тегів, жодних глобальних "очисток".
"""

from __future__ import annotations

import html
import re
from typing import Tuple

_CODE_BLOCK_RE = re.compile(r"```(?:\w+)?\n?([\s\S]*?)```", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_BOLD_UNDER_RE = re.compile(r"__(.+?)__")
_ITALIC_RE = re.compile(r"\*([^*]+)\*")
_ITALIC_UNDER_RE = re.compile(r"(?<![_])_([^_]+)_(?![_])")


def _placeholder(prefix: str, i: int) -> str:
    """Токен, який не змінює html.escape і не збігається з ** / * / _."""
    return f"\x00{prefix}{i}\x00"


def format_for_telegram(text: str) -> Tuple[str, str]:
    """
    Готує текст для відправки в Telegram. Один parse_mode — HTML.

    Порядок: витягнути block code → inline code → escape → bold/italic → повернути код.
    Курсив і жирний не застосовуються всередині коду. Перетину тегів немає.
    """
    if not text or not text.strip():
        return "", "HTML"

    raw = text.strip()

    # 1. Винести блоки коду в плейсхолдери
    blocks: list[str] = []

    def block_repl(m: re.Match) -> str:
        blocks.append(m.group(1))
        return _placeholder("B", len(blocks) - 1)

    s = _CODE_BLOCK_RE.sub(block_repl, raw)

    # 2. Винести inline-код в плейсхолдери
    inlines: list[str] = []

    def inline_repl(m: re.Match) -> str:
        inlines.append(m.group(1))
        return _placeholder("I", len(inlines) - 1)

    s = _INLINE_CODE_RE.sub(inline_repl, s)

    # 3. Екранувати звичайний текст (плейсхолдери залишаються)
    s = html.escape(s)

    # 4. Жирний і курсив тільки в не-коді
    s = _BOLD_RE.sub(r"<b>\1</b>", s)
    s = _BOLD_UNDER_RE.sub(r"<b>\1</b>", s)
    s = _ITALIC_RE.sub(r"<i>\1</i>", s)
    s = _ITALIC_UNDER_RE.sub(r"<i>\1</i>", s)

    # 5. Повернути блоки коду (вміст екрануємо при вставці)
    for i, content in enumerate(blocks):
        s = s.replace(_placeholder("B", i), f"<pre><code>{html.escape(content)}</code></pre>")

    # 6. Повернути inline-код
    for i, content in enumerate(inlines):
        s = s.replace(_placeholder("I", i), f"<code>{html.escape(content)}</code>")

    return s.strip(), "HTML"
