import asyncio
from datetime import datetime
from logger.telegram import send_telegram_message


class Logger:
    LEVEL_EMOJIS = {
        "INFO": "ℹ️",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
        "DEBUG": "🐛",
    }

    def __init__(
        self,
        default_level="INFO",
        log_to_file=True,
        log_to_telegram=False,
        log_file="logs.txt",
    ):
        """
        Initialize the logger.

        :param default_level: Default log level (INFO, WARNING, ERROR, etc.)
        :param log_to_file: Whether to save logs to a file
        :param log_to_telegram: Whether to send logs to Telegram
        :param log_file: Name of the log file
        """
        self.default_level = default_level
        self.log_to_file = log_to_file
        self.log_to_telegram = log_to_telegram
        self.log_file = log_file

    async def log(self, level: str, message: str, module: str = "General"):
        """
        Log a message.

        :param level: Log level (INFO, WARNING, ERROR, CRITICAL, DEBUG)
        :param message: Log message
        :param module: Module or component where the log originated
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = self.LEVEL_EMOJIS.get(level, "🔍")
        log_entry = f"{emoji} [{timestamp}] [{level}] [{module}] - {message}"

        # Print to console
        print(log_entry)

        # Write to file if enabled
        if self.log_to_file:
            try:
                with open(self.log_file, "a") as file:
                    file.write(log_entry + "\n")
            except IOError as e:
                print(f"Failed to write log to file: {e}")

        # Відправляємо в Telegram лише важливі рівні, щоб не спамити чат
        # Чому так: INFO/DEBUG можуть бути частими (наприклад кожне повідомлення користувача)
        if self.log_to_telegram and level in ("ERROR", "CRITICAL"):
            await self._send_to_telegram(log_entry)

    async def _send_to_telegram(self, message: str):
        """
        Send a log message to Telegram.

        :param message: Log message
        """
        await send_telegram_message(message)


if __name__ == "__main__":
    from logger import logger

    asyncio.run(
        logger.log(level="ERROR", module="Рассылка отчетов", message="Тестовый лог")
    )
