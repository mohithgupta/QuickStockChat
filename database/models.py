"""
Database models for conversation persistence.

This module contains SQLAlchemy ORM models for storing conversations
and messages in PostgreSQL/SQLite. Supports future multi-user functionality
and integrates with LangGraph checkpoint system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


# =============================================================================
# Base Class
# =============================================================================

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# =============================================================================
# Conversation Model
# =============================================================================

class Conversation(Base):
    """
    Model for storing conversation metadata.

    A conversation represents a chat session with multiple messages.
    Each conversation has a unique thread_id used by LangGraph for
    checkpoint management.
    """

    __tablename__ = "conversations"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # LangGraph integration
    thread_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique thread identifier from LangGraph"
    )

    # Future multi-user support (optional for now)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="User identifier for future multi-user support"
    )

    # Display metadata
    title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional conversation title for UI display"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when conversation was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when conversation was last updated"
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, thread_id={self.thread_id})>"


# =============================================================================
# Message Model
# =============================================================================

class Message(Base):
    """
    Model for storing individual messages within a conversation.

    Messages are stored as part of a conversation and represent
    individual prompts and responses in the chat.
    """

    __tablename__ = "messages"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to conversation
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to conversations table"
    )

    # LangGraph integration
    message_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Optional message identifier from LangGraph"
    )

    # Message content
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Message role: user, assistant, or system"
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Message content"
    )

    # Additional metadata (JSON)
    message_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Optional metadata as JSON (e.g., tokens, model used)"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when message was created"
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
