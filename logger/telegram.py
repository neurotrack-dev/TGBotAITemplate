import aiohttp
import asyncio

from config import TELEGRAM_BOT_FOR_REPORTS_KEY, TELEGRAM_GROUP_ID_FOR_LOGGER


async def send_telegram_message(message: str):
    """
    Send a message to Telegram using Bot API asynchronously.

    :param message: The message text to send
    """
    token = TELEGRAM_BOT_FOR_REPORTS_KEY
    chat_id = TELEGRAM_GROUP_ID_FOR_LOGGER
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientError as e:
            print(f"Failed to send message to Telegram: {e}")


if __name__ == "__main__":
    asyncio.run(send_telegram_message("test"))
