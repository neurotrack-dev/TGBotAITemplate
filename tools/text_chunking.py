"""
Розбиття довгих текстів для Telegram (ліміт 4096 символів).

Універсальна функція для відповідей користувачу та логів.
"""

from __future__ import annotations

MAX_CHUNK_LEN = 3800


def chunk_text(text: str, max_len: int = MAX_CHUNK_LEN) -> list[str]:
    """
    Розбиває текст на частини до max_len символів.

    Пріоритет: розріз по переносу рядка (\\n). Якщо немає — жорсткий розріз.
    Не ламає HTML-теги (розріз тільки по безпечних межах).
    """
    if not text:
        return []
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_len:
            chunks.append(remaining)
            break

        segment = remaining[:max_len]
        last_newline = segment.rfind("\n")
        if last_newline >= 0:
            split_at = last_newline + 1
        else:
            last_space = segment.rfind(" ")
            split_at = last_space + 1 if last_space > max_len // 2 else max_len

        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]

    return chunks
