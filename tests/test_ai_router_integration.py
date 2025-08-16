"""Integration tests for AI Router functionality.

These tests verify that the AI router can properly select providers,
handle fallbacks, and integrate with context management.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from plato.core.ai_router import AIRouter, AIRequest, AIProvider, TaskType, ChatMessage


@pytest.mark.integration
class TestAIRouterProviderSelection:
    """Test AI router provider selection logic."""

    async def test_provider_selection_by_task_type(self, ai_router: AIRouter):
        """Test that providers are selected based on task type strengths."""
        # Test code analysis task (should prefer Claude)
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Analyze this Python code")],
            task_type=TaskType.CODE_ANALYSIS,
        )

        # Mock available clients
        ai_router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT4: MagicMock(),
            AIProvider.GPT3_5: MagicMock(),
        }

        provider = ai_router.select_provider(request)
        # Code analysis should prefer Claude or GPT-4
        assert provider in [AIProvider.CLAUDE, AIProvider.GPT4]

    async def test_provider_selection_with_tools(self, ai_router: AIRouter):
        """Test provider selection when tools are required."""
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Use tools to analyze this")],
            task_type=TaskType.TOOL_USE,
            tools=[{"name": "test_tool", "parameters": {}}],
        )

        # Mock clients - only Claude and GPT4 support tools well
        ai_router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT4: MagicMock(),
            AIProvider.QWEN_LOCAL: MagicMock(),  # Doesn't support tools as well
        }

        provider = ai_router.select_provider(request)
        # Should prefer providers that support tools
        assert provider in [AIProvider.CLAUDE, AIProvider.GPT4]

    async def test_preferred_provider_override(self, ai_router: AIRouter):
        """Test that preferred provider is respected when available."""
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Test message")],
            preferred_provider=AIProvider.GPT3_5,
        )

        ai_router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT3_5: MagicMock(),
        }

        provider = ai_router.select_provider(request)
        assert provider == AIProvider.GPT3_5

    async def test_token_limit_consideration(self, ai_router: AIRouter):
        """Test that providers with insufficient token limits are penalized."""
        # Create a request that would exceed GPT-3.5's token limit
        long_content = (
            "This is a very long message. " * 1000
        )  # ~5000 chars ≈ 1250 tokens
        request = AIRequest(
            messages=[ChatMessage(role="user", content=long_content)],
            max_tokens=10000,  # This would exceed GPT-3.5's limit
            task_type=TaskType.CHAT,
        )

        ai_router._clients = {
            AIProvider.GPT3_5: MagicMock(),  # 16k token limit
            AIProvider.CLAUDE: MagicMock(),  # 100k token limit
        }

        provider = ai_router.select_provider(request)
        # Should prefer Claude due to higher token limit
        assert provider == AIProvider.CLAUDE


@pytest.mark.integration
class TestAIRouterClientInitialization:
    """Test AI router client initialization."""

    async def test_client_initialization_with_config(self, test_config: dict):
        """Test that clients are initialized based on configuration."""
        router = AIRouter(config=test_config)

        # Give clients time to initialize
        import asyncio

        await asyncio.sleep(0.2)

        # Should have clients for providers with API keys
        available_providers = await router.get_available_providers()

        # At minimum should have the providers we configured
        # (though they won't work with fake API keys)
        assert isinstance(available_providers, list)

        # Test capabilities are loaded
        for provider in [AIProvider.CLAUDE, AIProvider.GPT4, AIProvider.GPT3_5]:
            capability = router.get_provider_capabilities(provider)
            assert capability is not None
            assert capability.provider == provider
            assert len(capability.strengths) > 0


@pytest.mark.integration
class TestAIRouterChatFunctionality:
    """Test AI router chat functionality with mocked responses."""

    async def test_chat_with_mocked_claude(self, ai_router: AIRouter):
        """Test chat functionality with mocked Claude responses."""
        # Mock Claude client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello! I'm Claude.")]
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 15
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_client

        # Create request
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            preferred_provider=AIProvider.CLAUDE,
        )

        # Send chat request
        response = await ai_router.chat(request)

        assert response.content == "Hello! I'm Claude."
        assert response.provider == AIProvider.CLAUDE
        assert response.model == "claude-3-haiku-20240307"
        assert response.tokens_used == 25
        assert response.finish_reason == "stop"

    async def test_chat_with_mocked_openai(self, ai_router: AIRouter):
        """Test chat functionality with mocked OpenAI responses."""
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from GPT!"
        mock_choice.finish_reason = "stop"
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4-turbo-preview"
        mock_response.usage.total_tokens = 20

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.GPT4] = mock_client

        # Create request
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Hello")],
            preferred_provider=AIProvider.GPT4,
        )

        # Send chat request
        response = await ai_router.chat(request)

        assert response.content == "Hello from GPT!"
        assert response.provider == AIProvider.GPT4
        assert response.model == "gpt-4-turbo-preview"
        assert response.tokens_used == 20
        assert response.finish_reason == "stop"

    async def test_chat_fallback_on_error(self, ai_router: AIRouter):
        """Test that router falls back to alternative provider on error."""
        # Mock primary provider to fail
        mock_failing_client = AsyncMock()
        mock_failing_client.messages.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        ai_router._clients[AIProvider.CLAUDE] = mock_failing_client

        # Mock fallback provider to succeed
        mock_fallback_client = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Fallback response"
        mock_choice.finish_reason = "stop"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4-turbo-preview"
        mock_response.usage.total_tokens = 15

        mock_fallback_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        ai_router._clients[AIProvider.GPT4] = mock_fallback_client

        # Create request preferring Claude
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Test fallback")],
            preferred_provider=AIProvider.CLAUDE,
        )

        # Should fallback to GPT-4
        response = await ai_router.chat(request)

        assert response.content == "Fallback response"
        assert response.provider == AIProvider.GPT4

    async def test_chat_with_system_message(self, ai_router: AIRouter):
        """Test chat with system message handling."""
        # Mock Claude client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I understand the instructions.")]
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 20
        mock_response.usage.output_tokens = 10
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_client

        # Create request with system message
        request = AIRequest(
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Hello"),
            ],
            preferred_provider=AIProvider.CLAUDE,
        )

        response = await ai_router.chat(request)

        # Verify the call was made correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]

        # Should have system message in parameters
        assert "system" in call_args
        assert call_args["system"] == "You are a helpful assistant."

        # Messages should not include system message
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0]["role"] == "user"


@pytest.mark.integration
class TestAIRouterHealthChecks:
    """Test AI router health check functionality."""

    async def test_health_check_with_mocked_providers(self, ai_router: AIRouter):
        """Test health check functionality with mocked providers."""
        # Mock successful provider
        mock_successful_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="OK")]
        mock_response.model = "test-model"
        mock_response.usage.input_tokens = 1
        mock_response.usage.output_tokens = 1
        mock_response.stop_reason = "stop"

        mock_successful_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_successful_client

        # Mock failing provider
        mock_failing_client = AsyncMock()
        mock_failing_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        ai_router._clients[AIProvider.GPT4] = mock_failing_client

        # Run health check
        health = await ai_router.health_check()

        assert isinstance(health, dict)
        assert AIProvider.CLAUDE.value in health
        assert AIProvider.GPT4.value in health

        # Claude should be healthy, GPT-4 should not
        assert health[AIProvider.CLAUDE.value] is True
        assert health[AIProvider.GPT4.value] is False


@pytest.mark.integration
class TestAIRouterStreamingSupport:
    """Test AI router streaming functionality."""

    async def test_streaming_request_selection(self, ai_router: AIRouter):
        """Test that streaming requests prefer compatible providers."""
        request = AIRequest(
            messages=[ChatMessage(role="user", content="Stream this response")],
            stream=True,
            task_type=TaskType.CHAT,
        )

        # All major providers support streaming
        ai_router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT4: MagicMock(),
            AIProvider.GPT3_5: MagicMock(),
        }

        provider = ai_router.select_provider(request)

        # Should select a provider that supports streaming
        capability = ai_router.get_provider_capabilities(provider)
        assert capability.supports_streaming is True


@pytest.mark.integration
class TestAIRouterToolSupport:
    """Test AI router tool support functionality."""

    async def test_tool_request_handling(self, ai_router: AIRouter):
        """Test that tool requests are routed to compatible providers."""
        tools = [
            {
                "name": "get_weather",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                },
            }
        ]

        request = AIRequest(
            messages=[ChatMessage(role="user", content="What's the weather like?")],
            task_type=TaskType.TOOL_USE,
            tools=tools,
        )

        ai_router._clients = {
            AIProvider.CLAUDE: MagicMock(),
            AIProvider.GPT4: MagicMock(),
            AIProvider.QWEN_LOCAL: MagicMock(),  # Doesn't support tools as well
        }

        provider = ai_router.select_provider(request)

        # Should prefer providers with good tool support
        capability = ai_router.get_provider_capabilities(provider)
        assert capability.supports_tools is True
        assert provider in [AIProvider.CLAUDE, AIProvider.GPT4]
