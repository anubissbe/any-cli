"""Context Manager for maintaining conversation context across AI switches."""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

import tiktoken
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context that can be stored."""

    CONVERSATION = "conversation"
    PROJECT = "project"
    SESSION = "session"
    TOOL_RESULT = "tool_result"
    ERROR = "error"


class Priority(str, Enum):
    """Context priority levels for compression decisions."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ContextEntry:
    """Individual context entry."""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: ContextType = ContextType.CONVERSATION
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: Priority = Priority.MEDIUM
    tokens: int = 0
    compressed: bool = False

    def __post_init__(self):
        """Calculate token count after initialization."""
        if self.content and not self.tokens:
            self.tokens = self._count_tokens(self.content)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            encoder = tiktoken.get_encoding("cl100k_base")
            return len(encoder.encode(text))
        except Exception:
            # Fallback to rough estimate
            return len(text) // 4


class ConversationMessage(BaseModel):
    """Conversation message with enhanced metadata."""

    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    name: str | None = Field(None, description="Sender name")
    tool_calls: list[dict[str, Any]] | None = Field(None, description="Tool calls")
    tool_call_id: str | None = Field(None, description="Tool call ID")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    ai_provider: str | None = Field(None, description="AI provider that generated this")
    tokens: int = Field(0, description="Token count")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ContextWindow(BaseModel):
    """Context window configuration."""

    max_tokens: int = Field(32000, description="Maximum tokens in context")
    preserve_tokens: int = Field(
        4000, description="Tokens to preserve during compression"
    )
    compression_ratio: float = Field(0.3, description="Target compression ratio")
    min_entries: int = Field(10, description="Minimum entries to keep")


class ContextSession(BaseModel):
    """Context session containing all conversation state."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Session ID")
    created_at: float = Field(
        default_factory=time.time, description="Session creation time"
    )
    updated_at: float = Field(default_factory=time.time, description="Last update time")
    entries: list[ContextEntry] = Field(
        default_factory=list, description="Context entries"
    )
    messages: list[ConversationMessage] = Field(
        default_factory=list, description="Conversation messages"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Session metadata"
    )
    current_ai_provider: str | None = Field(None, description="Current AI provider")
    project_context: dict[str, Any] = Field(
        default_factory=dict, description="Project-specific context"
    )

    def total_tokens(self) -> int:
        """Calculate total tokens in session."""
        return sum(entry.tokens for entry in self.entries) + sum(
            msg.tokens for msg in self.messages
        )

    def update_timestamp(self):
        """Update the session timestamp."""
        self.updated_at = time.time()


class ContextManager:
    """Manages conversation context with intelligent compression."""

    def __init__(self, window_config: ContextWindow | None = None):
        """Initialize context manager."""
        self.window = window_config or ContextWindow()
        self.sessions: dict[str, ContextSession] = {}
        self.current_session_id: str | None = None
        self._compression_lock = asyncio.Lock()

        # Context compression strategies
        self.compression_strategies = {
            "summarize": self._summarize_context,
            "remove_old": self._remove_old_context,
            "compress_similar": self._compress_similar_context,
        }

    async def create_session(
        self,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new context session."""
        session_id = session_id or str(uuid4())

        session = ContextSession(id=session_id, metadata=metadata or {})

        self.sessions[session_id] = session
        self.current_session_id = session_id

        logger.info(f"Created new context session: {session_id}")
        return session_id

    def get_session(self, session_id: str | None = None) -> ContextSession | None:
        """Get a context session."""
        session_id = session_id or self.current_session_id
        return self.sessions.get(session_id) if session_id else None

    def set_current_session(self, session_id: str):
        """Set the current active session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")
        self.current_session_id = session_id

    async def add_message(
        self, message: ConversationMessage, session_id: str | None = None
    ) -> bool:
        """Add a conversation message to the session."""
        session = self.get_session(session_id)
        if not session:
            session_id = await self.create_session()
            session = self.get_session(session_id)

        # Calculate tokens if not provided
        if not message.tokens:
            message.tokens = self._count_tokens(message.content)

        session.messages.append(message)
        session.update_timestamp()

        # Check if compression is needed
        if session.total_tokens() > self.window.max_tokens:
            await self._compress_session(session)

        logger.debug(f"Added message to session {session.id}: {message.tokens} tokens")
        return True

    async def add_context(
        self,
        content: str,
        context_type: ContextType = ContextType.CONVERSATION,
        priority: Priority = Priority.MEDIUM,
        metadata: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> str:
        """Add context entry to the session."""
        session = self.get_session(session_id)
        if not session:
            session_id = await self.create_session()
            session = self.get_session(session_id)

        entry = ContextEntry(
            type=context_type,
            content=content,
            priority=priority,
            metadata=metadata or {},
        )

        session.entries.append(entry)
        session.update_timestamp()

        # Check if compression is needed
        if session.total_tokens() > self.window.max_tokens:
            await self._compress_session(session)

        logger.debug(
            f"Added context entry to session {session.id}: {entry.tokens} tokens"
        )
        return entry.id

    def get_conversation_history(
        self, session_id: str | None = None, max_messages: int | None = None
    ) -> list[ConversationMessage]:
        """Get conversation history from session."""
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session.messages
        if max_messages:
            messages = messages[-max_messages:]

        return messages

    def get_context_entries(
        self,
        context_type: ContextType | None = None,
        priority: Priority | None = None,
        session_id: str | None = None,
    ) -> list[ContextEntry]:
        """Get context entries with optional filtering."""
        session = self.get_session(session_id)
        if not session:
            return []

        entries = session.entries

        if context_type:
            entries = [e for e in entries if e.type == context_type]

        if priority:
            entries = [e for e in entries if e.priority == priority]

        return entries

    async def switch_ai_provider(
        self, new_provider: str, session_id: str | None = None
    ) -> bool:
        """Switch AI provider while preserving context."""
        session = self.get_session(session_id)
        if not session:
            return False

        old_provider = session.current_ai_provider
        session.current_ai_provider = new_provider
        session.update_timestamp()

        # Add context entry about the switch
        await self.add_context(
            content=f"Switched AI provider from {old_provider} to {new_provider}",
            context_type=ContextType.SESSION,
            priority=Priority.HIGH,
            metadata={"old_provider": old_provider, "new_provider": new_provider},
            session_id=session_id,
        )

        logger.info(
            f"Switched AI provider in session {session.id}: {old_provider} -> {new_provider}"
        )
        return True

    async def set_project_context(
        self, project_info: dict[str, Any], session_id: str | None = None
    ) -> bool:
        """Set project-specific context for the session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.project_context.update(project_info)
        session.update_timestamp()

        # Add context entry
        await self.add_context(
            content=f"Updated project context: {json.dumps(project_info, indent=2)}",
            context_type=ContextType.PROJECT,
            priority=Priority.HIGH,
            metadata=project_info,
            session_id=session_id,
        )

        return True

    def get_current_context_summary(
        self, session_id: str | None = None
    ) -> dict[str, Any]:
        """Get a summary of current context state."""
        session = self.get_session(session_id)
        if not session:
            return {}

        total_tokens = session.total_tokens()

        summary = {
            "session_id": session.id,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "total_tokens": total_tokens,
            "message_count": len(session.messages),
            "context_entries": len(session.entries),
            "current_ai_provider": session.current_ai_provider,
            "project_context": bool(session.project_context),
            "compression_needed": total_tokens > self.window.max_tokens,
            "context_usage": total_tokens / self.window.max_tokens,
        }

        # Context type breakdown
        context_types = {}
        for entry in session.entries:
            context_types[entry.type.value] = context_types.get(entry.type.value, 0) + 1
        summary["context_types"] = context_types

        # Priority breakdown
        priorities = {}
        for entry in session.entries:
            priorities[entry.priority.value] = (
                priorities.get(entry.priority.value, 0) + 1
            )
        summary["priorities"] = priorities

        return summary

    async def _compress_session(self, session: ContextSession):
        """Compress session context to fit within token limits."""
        async with self._compression_lock:
            logger.info(f"Starting compression for session {session.id}")

            initial_tokens = session.total_tokens()
            target_tokens = self.window.preserve_tokens

            # Apply compression strategies in order
            for strategy_name, strategy_func in self.compression_strategies.items():
                if session.total_tokens() <= target_tokens:
                    break

                logger.debug(f"Applying compression strategy: {strategy_name}")
                await strategy_func(session, target_tokens)

            final_tokens = session.total_tokens()
            compression_ratio = (initial_tokens - final_tokens) / initial_tokens

            logger.info(
                f"Compression complete: {initial_tokens} -> {final_tokens} tokens "
                f"({compression_ratio:.2%} reduction)"
            )

            # Add compression metadata
            await self.add_context(
                content=f"Context compressed: {initial_tokens} -> {final_tokens} tokens",
                context_type=ContextType.SESSION,
                priority=Priority.HIGH,
                metadata={
                    "compression_ratio": compression_ratio,
                    "initial_tokens": initial_tokens,
                    "final_tokens": final_tokens,
                    "timestamp": time.time(),
                },
                session_id=session.id,
            )

    async def _summarize_context(self, session: ContextSession, target_tokens: int):
        """Summarize old context entries."""
        # Group old entries by type
        old_entries = [
            e
            for e in session.entries
            if e.timestamp < time.time() - 3600  # Older than 1 hour
            and e.priority in [Priority.LOW, Priority.MEDIUM]
        ]

        if not old_entries:
            return

        # Group by type and create summaries
        type_groups = {}
        for entry in old_entries:
            if entry.type not in type_groups:
                type_groups[entry.type] = []
            type_groups[entry.type].append(entry)

        for context_type, entries in type_groups.items():
            if len(entries) < 3:  # Don't summarize small groups
                continue

            # Create summary
            total_tokens = sum(e.tokens for e in entries)
            summary_content = f"Summary of {len(entries)} {context_type.value} entries ({total_tokens} tokens):\n"

            # Add key points from each entry
            for entry in entries[:5]:  # Limit to first 5 entries
                summary_content += f"- {entry.content[:100]}...\n"

            # Create summary entry
            summary_entry = ContextEntry(
                type=context_type,
                content=summary_content,
                priority=Priority.MEDIUM,
                compressed=True,
                metadata={
                    "original_count": len(entries),
                    "original_tokens": total_tokens,
                    "summary_created": time.time(),
                },
            )

            # Replace original entries with summary
            session.entries = [e for e in session.entries if e not in entries]
            session.entries.append(summary_entry)

    async def _remove_old_context(self, session: ContextSession, target_tokens: int):
        """Remove old, low-priority context entries."""
        # Sort entries by priority and age
        sorted_entries = sorted(
            session.entries, key=lambda e: (e.priority.value, -e.timestamp)
        )

        # Remove low priority entries until we reach target
        current_tokens = session.total_tokens()
        entries_to_remove = []

        for entry in sorted_entries:
            if current_tokens <= target_tokens:
                break
            if entry.priority == Priority.LOW:
                entries_to_remove.append(entry)
                current_tokens -= entry.tokens

        # Remove entries
        for entry in entries_to_remove:
            session.entries.remove(entry)

        if entries_to_remove:
            logger.debug(f"Removed {len(entries_to_remove)} low-priority entries")

    async def _compress_similar_context(
        self, session: ContextSession, target_tokens: int
    ):
        """Compress similar context entries."""
        # Group entries by content similarity (simple approach)
        # This is a placeholder for more sophisticated similarity detection
        content_groups = {}

        for entry in session.entries:
            if entry.compressed or entry.priority == Priority.CRITICAL:
                continue

            # Simple grouping by first 50 characters
            key = entry.content[:50].lower().strip()
            if key not in content_groups:
                content_groups[key] = []
            content_groups[key].append(entry)

        # Compress groups with multiple similar entries
        for key, entries in content_groups.items():
            if len(entries) < 2:
                continue

            # Create compressed entry
            total_tokens = sum(e.tokens for e in entries)
            compressed_content = f"Compressed {len(entries)} similar entries:\n{key}..."

            compressed_entry = ContextEntry(
                type=entries[0].type,
                content=compressed_content,
                priority=max(e.priority for e in entries),
                compressed=True,
                metadata={
                    "original_count": len(entries),
                    "original_tokens": total_tokens,
                    "compression_key": key,
                },
            )

            # Replace with compressed entry
            for entry in entries:
                session.entries.remove(entry)
            session.entries.append(compressed_entry)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        try:
            encoder = tiktoken.get_encoding("cl100k_base")
            return len(encoder.encode(text))
        except Exception:
            return len(text) // 4  # Rough estimate

    async def export_session(self, session_id: str | None = None) -> dict[str, Any]:
        """Export session data for persistence."""
        session = self.get_session(session_id)
        if not session:
            return {}

        return session.model_dump()

    async def import_session(self, session_data: dict[str, Any]) -> str:
        """Import session data from persistence."""
        session = ContextSession(**session_data)
        self.sessions[session.id] = session

        logger.info(f"Imported session: {session.id}")
        return session.id

    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        sessions_to_remove = []

        for session_id, session in self.sessions.items():
            if session.updated_at < cutoff_time:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Cleaned up old session: {session_id}")

        return len(sessions_to_remove)
