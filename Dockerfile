FROM python:3.9-slim

# Чому так: менший образ, достатньо для aiogram/asyncio
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Спочатку залежності — краще кешується під час збірки
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Потім код
COPY . /app

# Чому так: в compose передаємо .env і запускаємо main.py
CMD ["python", "main.py"]
