"""Tests for context compression and memory management."""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

from plato.core.context_manager import (
    ContextManager,
    ContextWindow,
    ContextSession,
    ContextEntry,
    ConversationMessage,
    ContextType,
    Priority,
)


class TestContextCompression:
    """Test context compression and memory management."""

    @pytest.fixture
    def context_window(self):
        """Small context window for testing compression."""
        return ContextWindow(
            max_tokens=1000,
            preserve_tokens=300,
            compression_ratio=0.3,
            min_entries=5,
        )

    @pytest.fixture
    def context_manager(self, context_window):
        """Context manager with test configuration."""
        return ContextManager(window_config=context_window)

    @pytest.fixture
    def large_session_data(self):
        """Generate session data that exceeds token limits."""
        messages = []
        entries = []

        # Create many messages to exceed limits
        for i in range(20):
            msg = ConversationMessage(
                role="user" if i % 2 == 0 else "assistant",
                content=f"This is a long message with lots of content "
                * 10,  # ~150 tokens each
                tokens=150,
            )
            messages.append(msg)

        # Create many context entries
        for i in range(30):
            priority = (
                Priority.LOW if i < 10 else Priority.MEDIUM if i < 20 else Priority.HIGH
            )
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Context entry {i} with detailed information "
                * 8,  # ~100 tokens
                priority=priority,
                tokens=100,
                timestamp=time.time()
                - (30 - i) * 60,  # Older entries have earlier timestamps
            )
            entries.append(entry)

        return messages, entries

    @pytest.mark.asyncio
    async def test_automatic_compression_trigger(
        self, context_manager, large_session_data
    ):
        """Test that compression is triggered when token limit is exceeded."""
        messages, entries = large_session_data

        # Create session
        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        # Add data to exceed limits
        session.messages = messages
        session.entries = entries

        initial_tokens = session.total_tokens()
        assert initial_tokens > context_manager.window.max_tokens

        # Trigger compression by adding one more message
        await context_manager.add_message(
            ConversationMessage(role="user", content="Trigger compression", tokens=50),
            session_id=session_id,
        )

        # Compression should have occurred
        final_tokens = session.total_tokens()
        assert final_tokens < initial_tokens
        assert final_tokens <= context_manager.window.preserve_tokens

    @pytest.mark.asyncio
    async def test_priority_based_compression(self, context_manager):
        """Test that low priority entries are removed first."""
        session_id = await context_manager.create_session()

        # Add entries with different priorities
        high_priority_ids = []
        low_priority_ids = []

        for i in range(5):
            # High priority entries
            high_id = await context_manager.add_context(
                content=f"Critical information {i} " * 20,  # ~80 tokens
                priority=Priority.CRITICAL,
                session_id=session_id,
            )
            high_priority_ids.append(high_id)

            # Low priority entries
            low_id = await context_manager.add_context(
                content=f"Less important info {i} " * 20,  # ~80 tokens
                priority=Priority.LOW,
                session_id=session_id,
            )
            low_priority_ids.append(low_id)

        # Force compression
        session = context_manager.get_session(session_id)
        await context_manager._compress_session(session)

        # Check that high priority entries are preserved
        remaining_entries = session.entries
        remaining_ids = [entry.id for entry in remaining_entries]

        # More high priority entries should remain than low priority
        high_remaining = sum(1 for hid in high_priority_ids if hid in remaining_ids)
        low_remaining = sum(1 for lid in low_priority_ids if lid in remaining_ids)

        assert high_remaining > low_remaining

    @pytest.mark.asyncio
    async def test_age_based_compression(self, context_manager):
        """Test that older entries are compressed first."""
        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        # Add old entries
        old_timestamp = time.time() - 7200  # 2 hours ago
        old_entries = []
        for i in range(10):
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Old entry {i} " * 15,
                priority=Priority.MEDIUM,
                timestamp=old_timestamp + i * 60,
                tokens=60,
            )
            session.entries.append(entry)
            old_entries.append(entry)

        # Add recent entries
        recent_entries = []
        for i in range(5):
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Recent entry {i} " * 15,
                priority=Priority.MEDIUM,
                timestamp=time.time() - i * 60,
                tokens=60,
            )
            session.entries.append(entry)
            recent_entries.append(entry)

        # Force compression
        await context_manager._compress_session(session)

        # More recent entries should remain
        remaining_entries = set(session.entries)
        old_remaining = len([e for e in old_entries if e in remaining_entries])
        recent_remaining = len([e for e in recent_entries if e in remaining_entries])

        assert recent_remaining >= old_remaining

    @pytest.mark.asyncio
    async def test_summarization_compression(self, context_manager):
        """Test that old entries are summarized rather than deleted."""
        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        # Add many old entries of the same type
        old_timestamp = time.time() - 7200
        for i in range(10):
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Conversation entry {i} with detailed content " * 10,
                priority=Priority.MEDIUM,
                timestamp=old_timestamp + i * 60,
                tokens=100,
            )
            session.entries.append(entry)

        initial_count = len(session.entries)

        # Force summarization
        await context_manager._summarize_context(session, 500)

        # Should have fewer entries but include summaries
        final_count = len(session.entries)
        assert final_count < initial_count

        # Should have summary entries
        summary_entries = [e for e in session.entries if e.compressed]
        assert len(summary_entries) > 0

        # Summary should mention original count
        for summary in summary_entries:
            assert "entries" in summary.content.lower()

    @pytest.mark.asyncio
    async def test_similar_content_compression(self, context_manager):
        """Test compression of similar content entries."""
        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        # Add similar entries
        for i in range(5):
            entry = ContextEntry(
                type=ContextType.TOOL_RESULT,
                content="File operation result: success with detailed logs " * 8,
                priority=Priority.MEDIUM,
                tokens=80,
            )
            session.entries.append(entry)

        initial_count = len(session.entries)

        # Force similar content compression
        await context_manager._compress_similar_context(session, 200)

        # Should have compressed similar entries
        final_count = len(session.entries)
        assert final_count < initial_count

        # Should have compressed entries
        compressed_entries = [e for e in session.entries if e.compressed]
        assert len(compressed_entries) > 0

    @pytest.mark.asyncio
    async def test_compression_metadata_tracking(
        self, context_manager, large_session_data
    ):
        """Test that compression metadata is properly tracked."""
        messages, entries = large_session_data

        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        session.messages = messages
        session.entries = entries

        initial_tokens = session.total_tokens()

        # Force compression
        await context_manager._compress_session(session)

        # Should have compression metadata entry
        compression_entries = [
            e
            for e in session.entries
            if e.type == ContextType.SESSION and "compressed" in e.content.lower()
        ]
        assert len(compression_entries) > 0

        compression_entry = compression_entries[-1]  # Most recent
        assert "compression_ratio" in compression_entry.metadata
        assert "initial_tokens" in compression_entry.metadata
        assert "final_tokens" in compression_entry.metadata

    @pytest.mark.asyncio
    async def test_concurrent_compression_safety(self, context_manager):
        """Test that concurrent compression attempts are handled safely."""
        session_id = await context_manager.create_session()

        # Create large session that needs compression
        for i in range(50):
            await context_manager.add_context(
                content=f"Large content entry {i} " * 20,
                priority=Priority.MEDIUM,
                session_id=session_id,
            )

        session = context_manager.get_session(session_id)

        # Attempt concurrent compression
        tasks = [
            context_manager._compress_session(session),
            context_manager._compress_session(session),
            context_manager._compress_session(session),
        ]

        # Should complete without errors
        await asyncio.gather(*tasks, return_exceptions=True)

        # Session should be in valid state
        assert session.total_tokens() <= context_manager.window.preserve_tokens

    @pytest.mark.asyncio
    async def test_minimum_entries_preservation(self, context_manager):
        """Test that minimum number of entries are always preserved."""
        window_config = ContextWindow(
            max_tokens=500,
            preserve_tokens=100,
            min_entries=5,
        )
        manager = ContextManager(window_config=window_config)

        session_id = await manager.create_session()
        session = manager.get_session(session_id)

        # Add exactly minimum number of entries with high token count
        for i in range(5):
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Large entry {i} " * 50,  # ~200 tokens each
                priority=Priority.LOW,
                tokens=200,
            )
            session.entries.append(entry)

        # Force compression
        await manager._compress_session(session)

        # Should preserve minimum entries even if over token limit
        assert len(session.entries) >= window_config.min_entries

    @pytest.mark.asyncio
    async def test_compression_strategy_ordering(self, context_manager):
        """Test that compression strategies are applied in correct order."""
        session_id = await context_manager.create_session()
        session = context_manager.get_session(session_id)

        # Add mixed content that can be compressed different ways
        old_timestamp = time.time() - 7200

        # Old, low priority entries (should be removed first)
        for i in range(10):
            entry = ContextEntry(
                type=ContextType.CONVERSATION,
                content=f"Old low priority {i} " * 10,
                priority=Priority.LOW,
                timestamp=old_timestamp,
                tokens=100,
            )
            session.entries.append(entry)

        # Old, medium priority entries (should be summarized)
        for i in range(8):
            entry = ContextEntry(
                type=ContextType.TOOL_RESULT,
                content=f"Old medium priority tool result {i} " * 8,
                priority=Priority.MEDIUM,
                timestamp=old_timestamp + 60,
                tokens=80,
            )
            session.entries.append(entry)

        # Similar recent entries (should be compressed)
        for i in range(5):
            entry = ContextEntry(
                type=ContextType.ERROR,
                content="Recent similar error message with details " * 6,
                priority=Priority.MEDIUM,
                timestamp=time.time() - 300,
                tokens=60,
            )
            session.entries.append(entry)

        initial_count = len(session.entries)

        # Force full compression cycle
        await context_manager._compress_session(session)

        final_count = len(session.entries)
        assert final_count < initial_count

        # Verify compression artifacts exist
        has_summary = any(e.compressed for e in session.entries)
        assert has_summary

    @pytest.mark.asyncio
    async def test_compression_performance(self, context_manager):
        """Test compression performance with large datasets."""
        session_id = await context_manager.create_session()

        # Add many entries quickly
        start_time = time.time()
        for i in range(200):
            await context_manager.add_context(
                content=f"Performance test entry {i} " * 15,
                priority=Priority.MEDIUM if i % 2 else Priority.LOW,
                session_id=session_id,
            )

        # Compression should complete in reasonable time
        session = context_manager.get_session(session_id)
        compression_start = time.time()
        await context_manager._compress_session(session)
        compression_time = time.time() - compression_start

        # Should complete in under 5 seconds even with many entries
        assert compression_time < 5.0

        # Should achieve significant compression
        final_tokens = session.total_tokens()
        assert final_tokens <= context_manager.window.preserve_tokens

    @pytest.mark.asyncio
    async def test_critical_content_preservation(self, context_manager):
        """Test that critical content is never compressed away."""
        session_id = await context_manager.create_session()

        # Add critical entries that should never be compressed
        critical_content = "CRITICAL SYSTEM ERROR: Database connection failed"
        critical_id = await context_manager.add_context(
            content=critical_content,
            priority=Priority.CRITICAL,
            context_type=ContextType.ERROR,
            session_id=session_id,
        )

        # Add lots of low priority content to force compression
        for i in range(100):
            await context_manager.add_context(
                content=f"Low priority content {i} " * 20,
                priority=Priority.LOW,
                session_id=session_id,
            )

        session = context_manager.get_session(session_id)
        await context_manager._compress_session(session)

        # Critical content should still be present
        critical_entries = [e for e in session.entries if e.id == critical_id]
        assert len(critical_entries) == 1
        assert critical_entries[0].content == critical_content
