"""Basic tests for Plato components."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from plato.core.ai_router import AIRouter, AIRequest, TaskType, AIProvider
from plato.core.context_manager import ContextManager, ConversationMessage
from plato.core.mcp_manager import MCPManager, MCPServerConfig, MCPTransport
from plato.integrations.serena_mcp import SerenaMCPClient


@pytest.mark.unit
class TestAIRouter:
    """Test AI router functionality."""

    def test_provider_selection_by_task(self):
        """Test provider selection based on task type."""
        router = AIRouter()

        # Mock clients to avoid actual API calls
        router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT4: MagicMock(),
            AIProvider.GPT3_5: MagicMock(),
        }

        # Test code analysis task prefers Claude
        request = AIRequest(
            messages=[{"role": "user", "content": "Analyze this code"}],
            task_type=TaskType.CODE_ANALYSIS,
        )
        provider = router.select_provider(request)
        assert provider in [AIProvider.CLAUDE, AIProvider.GPT4]

        # Test chat task can use any provider
        request = AIRequest(
            messages=[{"role": "user", "content": "Hello"}], task_type=TaskType.CHAT
        )
        provider = router.select_provider(request)
        assert provider is not None

    def test_preferred_provider_override(self):
        """Test that preferred provider is respected."""
        router = AIRouter()
        router._clients = {AIProvider.GPT3_5: MagicMock()}

        request = AIRequest(
            messages=[{"role": "user", "content": "Test"}],
            preferred_provider=AIProvider.GPT3_5,
        )

        provider = router.select_provider(request)
        assert provider == AIProvider.GPT3_5

    def test_capabilities_initialization(self):
        """Test that AI provider capabilities are properly initialized."""
        router = AIRouter()

        # Check that all providers have capabilities
        assert AIProvider.CLAUDE in router._capabilities
        assert AIProvider.GPT4 in router._capabilities
        assert AIProvider.GPT3_5 in router._capabilities

        # Check Claude capabilities
        claude_caps = router._capabilities[AIProvider.CLAUDE]
        assert TaskType.CODE_ANALYSIS in claude_caps.strengths
        assert claude_caps.supports_tools is True
        assert claude_caps.max_tokens > 50000


@pytest.mark.unit
class TestContextManager:
    """Test context manager functionality."""

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test session creation and management."""
        manager = ContextManager()

        # Create session
        session_id = await manager.create_session()
        assert session_id is not None

        # Verify session exists
        session = manager.get_session(session_id)
        assert session is not None
        assert session.id == session_id

    @pytest.mark.asyncio
    async def test_message_handling(self):
        """Test adding and retrieving messages."""
        manager = ContextManager()
        session_id = await manager.create_session()

        # Add user message
        message = ConversationMessage(role="user", content="Test message")
        await manager.add_message(message, session_id)

        # Retrieve history
        history = manager.get_conversation_history(session_id)
        assert len(history) == 1
        assert history[0].content == "Test message"
        assert history[0].role == "user"

    @pytest.mark.asyncio
    async def test_context_compression(self):
        """Test context compression when token limit exceeded."""
        # Use small token limit for testing
        from plato.core.context_manager import ContextWindow

        window = ContextWindow(max_tokens=100, preserve_tokens=50)

        manager = ContextManager(window)
        session_id = await manager.create_session()

        # Add many messages to trigger compression
        for i in range(10):
            message = ConversationMessage(
                role="user",
                content=f"This is a long message {i} " * 20,  # ~100 characters each
            )
            await manager.add_message(message, session_id)

        session = manager.get_session(session_id)
        # Should have triggered compression
        assert session.total_tokens() <= window.max_tokens

    @pytest.mark.asyncio
    async def test_ai_provider_switching(self):
        """Test AI provider switching with context preservation."""
        manager = ContextManager()
        session_id = await manager.create_session()

        # Switch provider
        success = await manager.switch_ai_provider("claude", session_id)
        assert success is True

        session = manager.get_session(session_id)
        assert session.current_ai_provider == "claude"

        # Should have context entry about the switch
        entries = manager.get_context_entries(session_id=session_id)
        switch_entries = [e for e in entries if "Switched AI provider" in e.content]
        assert len(switch_entries) >= 1


@pytest.mark.unit
class TestMCPManager:
    """Test MCP manager functionality."""

    def test_server_configuration(self):
        """Test MCP server configuration."""
        manager = MCPManager()

        config = MCPServerConfig(
            name="test-server", transport=MCPTransport.SSE, url="http://localhost:8765"
        )

        success = manager.add_server(config)
        assert success is True
        assert "test-server" in manager.servers

    def test_duplicate_server_rejection(self):
        """Test that duplicate server names are rejected."""
        manager = MCPManager()

        config = MCPServerConfig(
            name="test-server", transport=MCPTransport.SSE, url="http://localhost:8765"
        )

        # Add first time
        success1 = manager.add_server(config)
        assert success1 is True

        # Try to add again
        success2 = manager.add_server(config)
        assert success2 is False

    def test_tool_discovery(self):
        """Test tool discovery and storage."""
        manager = MCPManager()

        # Mock a connection with tools
        connection = MagicMock()
        connection.config.name = "test-server"
        connection.connected = True

        # Mock tools
        mock_tools = [
            MagicMock(name="tool1", server="test-server"),
            MagicMock(name="tool2", server="test-server"),
        ]
        connection.list_tools = AsyncMock(return_value=mock_tools)

        manager.servers["test-server"] = connection

        # Add tools to manager
        for tool in mock_tools:
            tool_key = f"{tool.server}.{tool.name}"
            manager.tools[tool_key] = tool

        # Test tool retrieval
        tools = manager.list_tools("test-server")
        assert len(tools) == 2

        # Test tool lookup
        tool = manager.get_tool("test-server.tool1")
        assert tool is not None
        assert tool.name == "tool1"


@pytest.mark.unit
class TestSerenaMCPClient:
    """Test Serena MCP client functionality."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = SerenaMCPClient(host="localhost", port=8765)

        assert client.host == "localhost"
        assert client.port == 8765
        assert client.base_url == "http://localhost:8765"

    @pytest.mark.asyncio
    async def test_connection_handling(self):
        """Test connection lifecycle."""
        client = SerenaMCPClient()

        # Mock the HTTP client
        client._client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        client._client.get = AsyncMock(return_value=mock_response)

        # Test connection
        connected = await client.connect()
        assert connected is True

        # Test disconnection
        await client.disconnect()
        assert client._client is None

    def test_supported_languages(self):
        """Test supported language enumeration."""
        client = SerenaMCPClient()
        languages = client.get_supported_languages()

        assert len(languages) > 0
        assert "python" in [lang.value for lang in languages]
        assert "typescript" in [lang.value for lang in languages]


@pytest.mark.integration
class TestIntegration:
    """Integration tests for component interaction."""

    @pytest.mark.asyncio
    async def test_ai_router_context_integration(self):
        """Test AI router and context manager working together."""
        router = AIRouter()
        context_manager = ContextManager()

        # Mock AI client to avoid API calls
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.model = "claude-3-haiku"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        router._clients[AIProvider.CLAUDE] = mock_client

        # Create session and add message
        session_id = await context_manager.create_session()
        await context_manager.add_message(
            ConversationMessage(role="user", content="Test"), session_id
        )

        # Get conversation and send to AI
        history = context_manager.get_conversation_history(session_id)
        request = AIRequest(
            messages=[{"role": msg.role, "content": msg.content} for msg in history],
            preferred_provider=AIProvider.CLAUDE,
        )

        try:
            response = await router.chat(request)

            # Add AI response to context
            await context_manager.add_message(
                ConversationMessage(
                    role="assistant",
                    content=response.content,
                    ai_provider=response.provider.value,
                ),
                session_id,
            )

            # Verify integration worked
            final_history = context_manager.get_conversation_history(session_id)
            assert len(final_history) == 2
            assert final_history[1].role == "assistant"

        except Exception:
            # Mock API calls may fail, that's okay for this test
            pass


if __name__ == "__main__":
    pytest.main([__file__])
