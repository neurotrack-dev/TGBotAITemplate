FROM python:3.9-slim

# Чому так: менший образ, достатньо для aiogram/asyncio
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Спочатку залежності — краще кешується під час збірки
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Код (включно з entrypoint.sh). Entrypoint: alembic upgrade head → python main.py
COPY . /app
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
