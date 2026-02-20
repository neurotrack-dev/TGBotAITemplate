#!/bin/sh
# При старті контейнера: очікування БД (host/port з DATABASE_URL) → міграції → бот.
# main.py далі викликає init_db() — для вже застосованих міграцій це no-op.
set -e
echo "Waiting for database..."
python /app/scripts/wait_for_db.py
echo "Applying migrations..."
python -m alembic upgrade head
echo "Starting bot..."
exec python main.py
