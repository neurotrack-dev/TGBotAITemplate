"""
Alembic env.py — підключення до БД з config, метадані з моделей.

URL береться з config.settings.DATABASE_URL (sync-варіант для psycopg2).
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool

from config import settings
from db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    """URL для міграцій: sync-драйвер (psycopg2), бо Alembic за замовчуванням sync."""
    url = settings.DATABASE_URL
    if "+asyncpg" in url:
        url = url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    return url


def run_migrations_offline() -> None:
    """Міграції в offline (генерація SQL без підключення)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Міграції в online — підключення до БД з config."""
    connectable = create_engine(get_url(), poolclass=NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# offline: alembic upgrade head --sql (генерація SQL без підключення)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
