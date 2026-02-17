"""
ChatService — оркестрація діалогу, БД, AI.

Отримує/створює user, conversation, зберігає історію, передає в AI.
"""

from __future__ import annotations

import traceback

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Conversation, Message, User
from logger import logger
from services.ai_service import generate_reply
from tools.registry import get_tools

LAST_N_MESSAGES = 12
MAX_MESSAGES_PER_CONVERSATION = 200
AI_ERROR_FALLBACK = "Сталася помилка, спробуй ще раз."


class ChatService:
    """Сервіс для роботи з діалогами (user, conversation, messages, AI)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def ensure_user_and_conversation(
        self, telegram_id: int, username: str | None
    ) -> None:
        """
        При /start: створити/оновити User, створити активну Conversation якщо немає,
        проставити user.active_conversation_id. Без повідомлень.
        """
        user = await self._get_or_create_user(telegram_id, username)
        await self._get_or_create_active_conversation(user)

    async def process_message(
        self,
        telegram_id: int,
        username: str | None,
        user_text: str,
    ) -> str:
        """
        Повний цикл: user/conversation → історія → зберегти user msg → AI → зберегти assistant.
        """
        user = await self._get_or_create_user(telegram_id, username)
        conversation = await self._get_or_create_active_conversation(user)

        messages_db = await self._get_last_messages(conversation.id, n=LAST_N_MESSAGES)

        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=user_text,
        )
        self.session.add(user_msg)
        await self.session.flush()

        messages_for_ai = [
            {"role": m.role, "content": m.content}
            for m in messages_db
        ]
        messages_for_ai.append({"role": "user", "content": user_text})

        try:
            raw_reply = await generate_reply(messages_for_ai, tools=get_tools())
        except Exception as e:
            await logger.log(
                level="ERROR",
                module=__name__,
                message=f"AI помилка: {e}\n{traceback.format_exc()}",
            )
            raw_reply = AI_ERROR_FALLBACK

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=raw_reply,
        )
        self.session.add(assistant_msg)
        # commit робить UnitOfWork при виході з контексту
        return raw_reply

    async def _get_or_create_user(self, telegram_id: int, username: str | None) -> User:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            self.session.add(user)
            await self.session.flush()
        elif username is not None and user.username != username:
            user.username = username
        return user

    async def _get_or_create_active_conversation(self, user: User) -> Conversation:
        """
        Повертає активну conversation. Якщо в ній >= 200 повідомлень —
        закриває її (status='closed'), створює нову, оновлює user.active_conversation_id.
        """
        conv = None
        if user.active_conversation_id is not None:
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == user.active_conversation_id)
            )
            conv = result.scalars().first()

        if conv is None or conv.status != "active":
            result = await self.session.execute(
                select(Conversation)
                .where(Conversation.user_id == user.id, Conversation.status == "active")
                .order_by(desc(Conversation.id))
                .limit(1)
            )
            conv = result.scalars().first()
            if conv is None:
                conv = Conversation(user_id=user.id, status="active")
                self.session.add(conv)
                await self.session.flush()
                user.active_conversation_id = conv.id
                return conv

        count_result = await self.session.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conv.id)
        )
        count = count_result.scalar() or 0
        if count >= MAX_MESSAGES_PER_CONVERSATION:
            conv.status = "closed"
            new_conv = Conversation(user_id=user.id, status="active")
            self.session.add(new_conv)
            await self.session.flush()
            user.active_conversation_id = new_conv.id
            return new_conv
        return conv

    async def _get_last_messages(self, conversation_id: int, n: int = LAST_N_MESSAGES) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(n)
        )
        return list(result.scalars().all())
