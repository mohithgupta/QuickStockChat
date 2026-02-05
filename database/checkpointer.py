"""
Custom PostgreSQL checkpointer for LangGraph.

This module provides a database-backed checkpoint saver for LangGraph agents,
enabling conversation persistence across server restarts. It integrates with
the existing database models and session management.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional, Iterator, AsyncIterator, Any, List, Tuple
from sqlalchemy.orm import Session
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointTuple
from langgraph.checkpoint.memory import MemorySaver
from database.models import Conversation, Message
from database.session import SessionLocal


class PostgresCheckpointSaver(BaseCheckpointSaver):
    """
    PostgreSQL-backed checkpoint saver for LangGraph.

    This class implements the BaseCheckpointSaver interface to store
    conversation checkpoints in a PostgreSQL/SQLite database. It enables
    conversation persistence across server restarts and supports multi-round
    dialogues with context continuity.

    Attributes:
        serde: Optional serializer for checkpoint data (uses default if None)

    Example:
        from database.checkpointer import PostgresCheckpointSaver
        from langgraph.graph import StateGraph

        checkpointer = PostgresCheckpointSaver()
        graph = builder.compile(checkpointer=checkpointer)
    """

    def __init__(self, serde: Optional[Any] = None):
        """
        Initialize the PostgreSQL checkpointer.

        Args:
            serde: Optional serializer for checkpoint data.
                   If None, uses the default JsonPlusSerializer.
        """
        super().__init__(serde=serde)

    def _get_thread_id(self, config: dict) -> str:
        """
        Extract thread_id from configuration.

        Args:
            config: RunnableConfig dictionary containing configurable parameters

        Returns:
            str: The thread identifier

        Raises:
            ValueError: If thread_id is not found in config
        """
        try:
            return config["configurable"]["thread_id"]
        except (KeyError, TypeError) as e:
            raise ValueError(
                f"thread_id not found in config. Expected config['configurable']['thread_id'], "
                f"got: {config}"
            ) from e

    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> str:
        """
        Serialize checkpoint to JSON string.

        Args:
            checkpoint: Checkpoint dictionary to serialize

        Returns:
            str: JSON-serialized checkpoint data
        """
        if self.serde:
            return self.serde.dumps_typed(checkpoint)
        # Use default JSON serialization if no custom serializer
        return json.dumps(checkpoint, default=str)

    def _deserialize_checkpoint(self, data: str) -> Checkpoint:
        """
        Deserialize JSON string to checkpoint.

        Args:
            data: JSON string containing checkpoint data

        Returns:
            Checkpoint: Deserialized checkpoint dictionary
        """
        if self.serde:
            return self.serde.loads_typed(data)
        # Use default JSON deserialization if no custom serializer
        return json.loads(data)

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """
        Retrieve a checkpoint tuple for the given thread configuration.

        Args:
            config: RunnableConfig containing thread_id in configurable section

        Returns:
            Optional[CheckpointTuple]: Checkpoint tuple if found, None otherwise
        """
        thread_id = self._get_thread_id(config)

        with SessionLocal() as db:
            # Query the most recent checkpoint for this thread
            conversation = db.query(Conversation).filter(
                Conversation.thread_id == thread_id
            ).order_by(Conversation.updated_at.desc()).first()

            if not conversation:
                return None

            # Get the last message which contains the checkpoint data
            # We store checkpoint in message_metadata with a special key
            last_message = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at.desc()).first()

            if not last_message or not last_message.message_metadata:
                return None

            # Extract checkpoint from metadata
            checkpoint_data = last_message.message_metadata.get("checkpoint")
            if not checkpoint_data:
                return None

            # Deserialize checkpoint
            checkpoint = self._deserialize_checkpoint(checkpoint_data)

            # Create CheckpointTuple
            checkpoint_tuple = CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "thread_ts": conversation.updated_at.isoformat()
                    }
                },
                checkpoint=checkpoint,
                metadata=last_message.message_metadata.get("metadata", {}),
                parent_config=last_message.message_metadata.get("parent_config"),
            )

            return checkpoint_tuple

    def list(self, config: dict, *, limit: int = 10) -> Iterator[CheckpointTuple]:
        """
        List checkpoints for the given thread configuration.

        Args:
            config: RunnableConfig containing thread_id in configurable section
            limit: Maximum number of checkpoints to return (default: 10)

        Yields:
            CheckpointTuple: Checkpoint tuples in reverse chronological order
        """
        thread_id = self._get_thread_id(config)

        with SessionLocal() as db:
            # Query conversations for this thread
            conversations = db.query(Conversation).filter(
                Conversation.thread_id == thread_id
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()

            for conversation in conversations:
                # Get the last message for each conversation
                last_message = db.query(Message).filter(
                    Message.conversation_id == conversation.id
                ).order_by(Message.created_at.desc()).first()

                if not last_message or not last_message.message_metadata:
                    continue

                checkpoint_data = last_message.message_metadata.get("checkpoint")
                if not checkpoint_data:
                    continue

                checkpoint = self._deserialize_checkpoint(checkpoint_data)

                checkpoint_tuple = CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": thread_id,
                            "thread_ts": conversation.updated_at.isoformat()
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=last_message.message_metadata.get("metadata", {}),
                    parent_config=last_message.message_metadata.get("parent_config"),
                )

                yield checkpoint_tuple

    def put(self, config: dict, checkpoint: Checkpoint) -> dict:
        """
        Store a checkpoint for the given thread configuration.

        Args:
            config: RunnableConfig containing thread_id in configurable section
            checkpoint: Checkpoint dictionary to store

        Returns:
            dict: Updated configuration with timestamp
        """
        thread_id = self._get_thread_id(config)

        with SessionLocal() as db:
            # Find or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.thread_id == thread_id
            ).first()

            if not conversation:
                # Create new conversation
                conversation = Conversation(
                    thread_id=thread_id,
                    title=f"Conversation {thread_id}"
                )
                db.add(conversation)
                db.flush()  # Get the ID

            # Serialize checkpoint
            checkpoint_data = self._serialize_checkpoint(checkpoint)

            # Create or update checkpoint message
            # We store checkpoints as system messages with metadata
            checkpoint_message = Message(
                conversation_id=conversation.id,
                role="system",
                content="[Checkpoint]",
                message_metadata={
                    "checkpoint": checkpoint_data,
                    "metadata": checkpoint.get("metadata", {}),
                    "parent_config": config.get("parent_config"),
                    "checkpoint_type": "langgraph_checkpoint"
                }
            )

            db.add(checkpoint_message)
            db.commit()

            # Return updated config
            return {
                "configurable": {
                    "thread_id": thread_id,
                    "thread_ts": datetime.now(timezone.utc).isoformat()
                }
            }

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        """
        Async version of get_tuple.

        Args:
            config: RunnableConfig containing thread_id

        Returns:
            Optional[CheckpointTuple]: Checkpoint tuple if found
        """
        return await asyncio.to_thread(self.get_tuple, config)

    async def alist(self, config: dict, *, limit: int = 10) -> AsyncIterator[CheckpointTuple]:
        """
        Async version of list.

        Args:
            config: RunnableConfig containing thread_id
            limit: Maximum number of checkpoints to return

        Yields:
            CheckpointTuple: Checkpoint tuples in reverse chronological order
        """
        # Run the synchronous list method in a thread pool and collect results
        result = await asyncio.to_thread(self.list, config, limit=limit)
        # Yield each result asynchronously
        for item in result:
            yield item

    async def aput(self, config: dict, checkpoint: Checkpoint) -> dict:
        """
        Async version of put.

        Args:
            config: RunnableConfig containing thread_id
            checkpoint: Checkpoint dictionary to store

        Returns:
            dict: Updated configuration with timestamp
        """
        return await asyncio.to_thread(self.put, config, checkpoint)

    def put_writes(
        self,
        config: dict,
        writes: List[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """
        Store intermediate writes for a checkpoint.

        This method stores writes that occur during checkpoint execution,
        enabling support for concurrent operations and checkpoint recovery.

        Args:
            config: RunnableConfig containing thread_id
            writes: List of (channel, value) tuples to store
            task_id: Unique identifier for the task
            task_path: Path identifier for nested tasks
        """
        thread_id = self._get_thread_id(config)

        with SessionLocal() as db:
            # Find the conversation
            conversation = db.query(Conversation).filter(
                Conversation.thread_id == thread_id
            ).first()

            if not conversation:
                return

            # Store writes as metadata in a system message
            writes_message = Message(
                conversation_id=conversation.id,
                role="system",
                content="[Writes]",
                message_metadata={
                    "writes": writes,
                    "task_id": task_id,
                    "task_path": task_path,
                    "writes_type": "langgraph_writes"
                }
            )

            db.add(writes_message)
            db.commit()

    async def aput_writes(
        self,
        config: dict,
        writes: List[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """
        Async version of put_writes.

        Args:
            config: RunnableConfig containing thread_id
            writes: List of (channel, value) tuples to store
            task_id: Unique identifier for the task
            task_path: Path identifier for nested tasks
        """
        await asyncio.to_thread(self.put_writes, config, writes, task_id, task_path)

    def delete_thread(self, thread_id: str) -> None:
        """
        Delete a conversation thread and all associated data.

        Args:
            thread_id: The thread identifier to delete
        """
        with SessionLocal() as db:
            # Find the conversation
            conversation = db.query(Conversation).filter(
                Conversation.thread_id == thread_id
            ).first()

            if not conversation:
                return

            # Delete associated messages (cascade should handle this, but be explicit)
            db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).delete()

            # Delete the conversation
            db.delete(conversation)
            db.commit()

    async def adelete_thread(self, thread_id: str) -> None:
        """
        Async version of delete_thread.

        Args:
            thread_id: The thread identifier to delete
        """
        await asyncio.to_thread(self.delete_thread, thread_id)


# For backwards compatibility and easier testing
def create_postgres_checkpointer(serde: Optional[Any] = None) -> PostgresCheckpointSaver:
    """
    Factory function to create a PostgreSQL checkpointer instance.

    Args:
        serde: Optional serializer for checkpoint data

    Returns:
        PostgresCheckpointSaver: Configured checkpointer instance

    Example:
        checkpointer = create_postgres_checkpointer()
        agent = create_agent(model, tools, checkpointer=checkpointer)
    """
    return PostgresCheckpointSaver(serde=serde)
