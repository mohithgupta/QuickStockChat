"""
Initial migration for conversation persistence.

This migration creates the database schema for storing conversations and messages,
enabling persistent chat history across server restarts.

Revision ID: 001_initial
Revises:
Create Date: 2026-02-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create initial database schema for conversations and messages.

    This creates two tables:
    - conversations: Stores conversation metadata (thread_id, timestamps)
    - messages: Stores individual messages with relationship to conversations

    Schema supports future multi-user functionality with optional user_id field.
    """
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=False, comment='Unique thread identifier from LangGraph'),
        sa.Column('user_id', sa.String(length=255), nullable=True, comment='User identifier for future multi-user support'),
        sa.Column('title', sa.String(length=500), nullable=True, comment='Optional conversation title for UI display'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW'), nullable=False, comment='Timestamp when conversation was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW'), nullable=False, comment='Timestamp when conversation was last updated'),
        sa.PrimaryKeyConstraint('id', name='conversations_pkey'),
        comment='Conversation metadata for chat sessions'
    )
    op.create_index('ix_conversations_thread_id', 'conversations', ['thread_id'], unique=True)
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'], unique=False)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False, comment='Foreign key to conversations table'),
        sa.Column('message_id', sa.String(length=255), nullable=True, comment='Optional message identifier from LangGraph'),
        sa.Column('role', sa.String(length=50), nullable=False, comment='Message role: user, assistant, or system'),
        sa.Column('content', sa.Text(), nullable=False, comment='Message content'),
        sa.Column('message_metadata', sa.JSON(), nullable=True, comment='Optional metadata as JSON (e.g., tokens, model used)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW'), nullable=False, comment='Timestamp when message was created'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='messages_conversation_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='messages_pkey'),
        comment='Individual messages within conversations'
    )
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'], unique=False)
    op.create_index('ix_messages_role', 'messages', ['role'], unique=False)


def downgrade() -> None:
    """
    Drop the conversation and messages tables.

    This reverses the migration by removing the tables in reverse order
    (messages first due to foreign key constraint, then conversations).
    """
    # Drop messages table first (due to foreign key)
    op.drop_index('ix_messages_role', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_index('ix_conversations_thread_id', table_name='conversations')
    op.drop_table('conversations')
