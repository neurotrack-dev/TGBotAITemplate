"""
Async session factory, Unit of Work — один шар транзакцій.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings
from db.models import Base


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class UnitOfWork:
    """
    Unit of Work: одна транзакція на весь сценарій.

    При виході: commit при успіху, rollback при помилці, завжди close.
    Сервіси не роблять commit — лише flush() коли потрібен id.
    """

    session: AsyncSession

    async def __aenter__(self) -> UnitOfWork:
        self.session = async_session_factory()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Низькорівневий контекст сесії без авто-commit. Для UoW використовуй UnitOfWork()."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Створює таблиці в БД. Викликати при старті бота."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
