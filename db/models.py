"""
SQLAlchemy models для історії діалогу.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    active_conversation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conversations.id", use_alter=True, name="fk_user_active_conversation"),
        nullable=True,
    )

    active_conversation: Mapped[Optional["Conversation"]] = relationship(
        "Conversation",
        foreign_keys=[active_conversation_id],
        back_populates="user_active",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        foreign_keys="Conversation.user_id",
        back_populates="user",
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="active")

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="conversations"
    )
    user_active: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys="User.active_conversation_id",
        back_populates="active_conversation",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(50))  # user, assistant, system
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
