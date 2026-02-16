import html
import aiohttp
import asyncio

from config import settings
from tools.text_chunking import chunk_text


async def send_telegram_message(message: str):
    """
    Send a message to Telegram using Bot API asynchronously.
    Long messages are split into chunks (3800 chars) to respect Telegram limit.
    """
    escaped = html.escape(message, quote=False)

    token = settings.BOT_TOKEN
    chat_id = settings.TELEGRAM_GROUP_ID_FOR_LOGGER
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    async with aiohttp.ClientSession() as session:
        for chunk in chunk_text(escaped):
            try:
                payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"}
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    await response.json()
            except aiohttp.ClientError as e:
                print(f"Failed to send message to Telegram: {e}")


if __name__ == "__main__":
    asyncio.run(send_telegram_message("test"))
