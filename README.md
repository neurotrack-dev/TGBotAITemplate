# Telegram AI Bot — архітектурний шаблон

Обучальний макет Telegram-бота на Python (aiogram 3.x) з AI-сервісом та підтримкою tools (function calling).

**Ціль:** показати модульну архітектуру, готу до розширення. Без бізнес-логіки.

## Quickstart

```bash
cp .env.example .env
pip install -r requirements.txt
python main.py
```

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

## Що де лежить

- **handlers/** — тільки Telegram-логіка: команди, callback, повідомлення. Не містить AI чи форматування.
- **services/** — бізнес/AI: `generate_reply()`, виклики LLM. Без залежності від aiogram.
- **prompts/** — системні промпти для LLM (англійською), щоб редагувати без правок коду.
- **formatters/** — адаптація тексту під Telegram: HTML, escaping, fallback.
- **db/** — PostgreSQL + SQLAlchemy async: User, Conversation, Message, сесії.
- **tools/** — function calling: реєстр, контракт (name, schema, handler), приклади.
- **config.py** — налаштування з .env (pydantic-settings).
- **logger/** — логування (консоль + опціонально відправка в Telegram)

## Структура проекту

```
├── main.py              # Точка входу
├── config.py            # pydantic-settings
├── logger/              # Логування
│   ├── logger_module.py # Logger (файл, Telegram)
│   └── telegram.py      # Відправка логів у чат
├── handlers/
│   ├── start.py         # /start — привітання
│   └── chat.py          # Текстові повідомлення → AI
├── services/
│   ├── ai_service.py    # generate_reply(messages, tools)
│   └── chat_service.py  # ChatService: user/conversation, історія, AI
├── prompts/
│   └── system_prompt.txt # System prompt для LLM
├── formatters/
│   └── tg_formatter.py  # HTML, escape, markdown→теги
├── db/
│   ├── models.py        # User, Conversation, Message
│   └── session.py       # get_async_session, init_db
├── tools/
│   ├── base.py          # Tool(name, description, schema, handler)
│   ├── registry.py      # Реєстр tools
│   └── sample_tool.py   # get_current_time
├── .env.example
└── requirements.txt
```

## Flow

1. `/start` → привітання (без клавіатури)
2. Будь-яке текстове повідомлення (крім команд `/...`) → ChatService (user, conversation, історія)
3. AI генерує відповідь через `generate_reply(messages, tools)` (історія з БД)
4. Відповідь форматується (HTML) і відправляється; при TelegramBadRequest — plain text

## Встановлення

```bash
# Клонування (якщо з git)
git clone <repo>
cd <TelegramBot>

# Віртуальне середовище
python -m venv venv
source venv/bin/activate  # Linux/macOS
# або: venv\Scripts\activate  # Windows

# Залежності
pip install -r requirements.txt
```

## Запуск

```bash
# Скопіюйте .env.example в .env і додайте BOT_TOKEN
cp .env.example .env
# Відредагуйте .env

python main.py
```

## Змінні оточення

| Змінна         | Обов'язкова | Опис                          |
|----------------|-------------|-------------------------------|
| `BOT_TOKEN`    | Так         | Токен з @BotFather            |
| `OPENAI_API_KEY` | Ні        | Для OpenAI (поки mock)        |
| `TELEGRAM_BOT_FOR_REPORTS_KEY` | Ні | Для logger — відправка логів у Telegram |
| `TELEGRAM_GROUP_ID_FOR_LOGGER` | Ні | ID чату для логів              |
| `DATABASE_URL` | Ні | PostgreSQL (postgresql+asyncpg://...) |

## Розширення

- **Підключення OpenAI:** замінити mock у `services/ai_service.py` на виклик `openai.ChatCompletion.create()`
- **Новий tool:** створити файл у `tools/`, викликати `register_tool()`, додати імпорт у `tools.registry.register_all_tools()`
- **Новий handler:** додати файл у `handlers/`, підключити роутер у `main.py`
