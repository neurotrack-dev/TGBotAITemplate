#!/bin/sh
# При старті контейнера: спочатку міграції (таблиці/зміни схеми), потім бот.
# main.py далі викликає init_db() — для вже застосованих міграцій це no-op.
set -e
echo "Applying migrations..."
python -m alembic upgrade head
echo "Starting bot..."
exec python main.py
