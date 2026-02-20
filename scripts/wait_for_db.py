#!/usr/bin/env python3
"""
Очікування доступності БД: парсинг DATABASE_URL (host, port), перевірка DNS + TCP.
Використовується в entrypoint перед alembic upgrade head.
"""
import os
import socket
import sys
import time
from urllib.parse import urlparse


def main() -> None:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        print("DATABASE_URL is not set", file=sys.stderr)
        sys.exit(1)

    # Підтримка postgresql+asyncpg:// та postgresql://
    if "://" in url:
        # urlparse коректно обробляє scheme з '+' (hostname/port з netloc)
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
    else:
        host, port = "localhost", 5432

    timeout_sec = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))
    interval_sec = float(os.environ.get("DB_WAIT_INTERVAL", "1"))
    deadline = time.monotonic() + timeout_sec

    print(f"Waiting for DB at {host}:{port} (timeout {timeout_sec}s)...", flush=True)
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                pass
            print(f"DB at {host}:{port} is reachable.", flush=True)
            return
        except (socket.error, socket.timeout, OSError):
            time.sleep(interval_sec)

    print(f"Timeout: DB at {host}:{port} did not become reachable.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
