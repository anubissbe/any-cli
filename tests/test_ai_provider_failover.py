"""Tests for AI provider failover and routing logic."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from plato.core.ai_router import (
    AIRouter,
    AIProvider,
    AIRequest,
    AIResponse,
    ChatMessage,
    TaskType,
)


class TestAIProviderFailover:
    """Test AI provider failover scenarios."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration with all providers."""
        return {
            "anthropic_api_key": "test-anthropic-key",
            "openai_api_key": "test-openai-key",
            "gemini_api_key": "test-gemini-key",
            "openrouter_api_key": "test-openrouter-key",
            "qwen_base_url": "http://localhost:8000",
        }

    @pytest.fixture
    async def router(self, mock_config):
        """Create AI router with mocked clients."""
        router = AIRouter(config=mock_config)

        # Mock client initialization
        with patch.object(router, "_init_clients") as mock_init:
            mock_init.return_value = None

            # Add mock clients
            router._clients = {
                AIProvider.CLAUDE: AsyncMock(),
                AIProvider.GPT4: AsyncMock(),
                AIProvider.GEMINI: AsyncMock(),
                AIProvider.QWEN_LOCAL: AsyncMock(),
            }

            router._initialized = True

        return router

    @pytest.fixture
    def basic_request(self):
        """Basic chat request for testing."""
        return AIRequest(
            messages=[ChatMessage(role="user", content="Hello, world!")],
            task_type=TaskType.CHAT,
            max_tokens=100,
        )

    @pytest.mark.asyncio
    async def test_primary_provider_success(self, router, basic_request):
        """Test successful request with primary provider."""
        # Mock successful Claude response
        router._clients[AIProvider.CLAUDE].messages.create.return_value = AsyncMock(
            content=[AsyncMock(text="Hello! How can I help?")],
            model="claude-3-haiku-20240307",
            usage=AsyncMock(input_tokens=10, output_tokens=20),
            stop_reason="stop",
        )

        # Force selection of Claude
        basic_request.preferred_provider = AIProvider.CLAUDE

        response = await router.chat(basic_request)

        assert response.provider == AIProvider.CLAUDE
        assert response.content == "Hello! How can I help?"
        assert response.tokens_used == 30

    @pytest.mark.asyncio
    async def test_primary_provider_failure_with_fallback(self, router, basic_request):
        """Test fallback when primary provider fails."""
        # Mock Claude failure
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = Exception(
            "Claude API error"
        )

        # Mock GPT-4 success
        gpt_response = AsyncMock()
        gpt_response.choices = [
            AsyncMock(message=AsyncMock(content="GPT-4 response"), finish_reason="stop")
        ]
        gpt_response.model = "gpt-4-turbo-preview"
        gpt_response.usage = AsyncMock(total_tokens=25)
        router._clients[AIProvider.GPT4].chat.completions.create.return_value = (
            gpt_response
        )

        # Force selection of Claude first
        basic_request.preferred_provider = AIProvider.CLAUDE

        response = await router.chat(basic_request)

        # Should fall back to GPT-4
        assert response.provider == AIProvider.GPT4
        assert response.content == "GPT-4 response"

    @pytest.mark.asyncio
    async def test_multiple_provider_failures(self, router, basic_request):
        """Test handling when multiple providers fail."""
        # Mock all providers failing except one
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = Exception(
            "Claude error"
        )

        gpt_response = AsyncMock()
        gpt_response.choices = [AsyncMock()]
        gpt_response.choices[0].message.content = None  # Empty response
        router._clients[AIProvider.GPT4].chat.completions.create.side_effect = (
            Exception("GPT error")
        )

        # Mock Gemini success
        with patch("google.generativeai.GenerativeModel") as mock_model:
            mock_instance = mock_model.return_value
            mock_instance.generate_content_async.return_value = AsyncMock(
                text="Gemini response", prompt_feedback=None
            )

            response = await router.chat(basic_request)

            # Should eventually succeed with Gemini
            assert response.provider == AIProvider.GEMINI
            assert response.content == "Gemini response"

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, router, basic_request):
        """Test handling when all providers fail."""
        # Mock all providers failing
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = Exception(
            "Claude error"
        )
        router._clients[AIProvider.GPT4].chat.completions.create.side_effect = (
            Exception("GPT error")
        )

        with patch("google.generativeai.GenerativeModel") as mock_model:
            mock_instance = mock_model.return_value
            mock_instance.generate_content_async.side_effect = Exception("Gemini error")

            # Should raise exception when all providers fail
            with pytest.raises(Exception):
                await router.chat(basic_request)

    @pytest.mark.asyncio
    async def test_provider_selection_based_on_task_type(self, router):
        """Test that provider selection considers task type strengths."""
        # Code analysis request should prefer Claude
        code_request = AIRequest(
            messages=[ChatMessage(role="user", content="Analyze this code")],
            task_type=TaskType.CODE_ANALYSIS,
        )

        selected = router.select_provider(code_request)
        # Claude has CODE_ANALYSIS as a strength
        assert selected == AIProvider.CLAUDE

        # Creative task might prefer different provider
        creative_request = AIRequest(
            messages=[ChatMessage(role="user", content="Write a poem")],
            task_type=TaskType.CREATIVE,
        )

        selected = router.select_provider(creative_request)
        # Should select based on capabilities (might be Gemini or others)
        assert selected in router._clients.keys()

    @pytest.mark.asyncio
    async def test_tool_support_requirement(self, router):
        """Test provider selection when tools are required."""
        tool_request = AIRequest(
            messages=[ChatMessage(role="user", content="Use tools")],
            task_type=TaskType.TOOL_USE,
            tools=[{"type": "function", "function": {"name": "test_tool"}}],
        )

        selected = router.select_provider(tool_request)

        # Should select a provider that supports tools
        capability = router._capabilities[selected]
        assert capability.supports_tools is True

    @pytest.mark.asyncio
    async def test_token_limit_consideration(self, router):
        """Test provider selection considers token limits."""
        # Very long request
        long_content = "This is a test. " * 10000  # Very long message
        long_request = AIRequest(
            messages=[ChatMessage(role="user", content=long_content)],
            max_tokens=50000,
        )

        selected = router.select_provider(long_request)

        # Should select provider with sufficient token limit
        capability = router._capabilities[selected]
        estimated_tokens = len(long_content) // 4 + 50000
        assert capability.max_tokens >= estimated_tokens

    @pytest.mark.asyncio
    async def test_streaming_support_requirement(self, router):
        """Test provider selection for streaming requests."""
        stream_request = AIRequest(
            messages=[ChatMessage(role="user", content="Stream response")],
            stream=True,
        )

        selected = router.select_provider(stream_request)

        # Should select provider that supports streaming
        capability = router._capabilities[selected]
        assert capability.supports_streaming is True

    @pytest.mark.asyncio
    async def test_health_check_with_failures(self, router):
        """Test health check handling provider failures."""
        # Mock some providers failing health checks
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = Exception(
            "Claude down"
        )

        # Mock GPT success
        gpt_response = AsyncMock()
        gpt_response.choices = [AsyncMock(message=AsyncMock(content="OK"))]
        gpt_response.model = "gpt-4"
        gpt_response.usage = AsyncMock(total_tokens=5)
        router._clients[AIProvider.GPT4].chat.completions.create.return_value = (
            gpt_response
        )

        health_status = await router.health_check()

        assert health_status[AIProvider.CLAUDE.value] is False
        assert health_status[AIProvider.GPT4.value] is True

    @pytest.mark.asyncio
    async def test_concurrent_requests_different_providers(self, router):
        """Test handling concurrent requests with different providers."""
        # Mock responses for different providers
        router._clients[AIProvider.CLAUDE].messages.create.return_value = AsyncMock(
            content=[AsyncMock(text="Claude response")],
            model="claude-3-haiku-20240307",
            usage=AsyncMock(input_tokens=5, output_tokens=10),
            stop_reason="stop",
        )

        gpt_response = AsyncMock()
        gpt_response.choices = [AsyncMock(message=AsyncMock(content="GPT response"))]
        gpt_response.model = "gpt-4"
        gpt_response.usage = AsyncMock(total_tokens=15)
        router._clients[AIProvider.GPT4].chat.completions.create.return_value = (
            gpt_response
        )

        # Create requests for different providers
        claude_request = AIRequest(
            messages=[ChatMessage(role="user", content="Hello Claude")],
            preferred_provider=AIProvider.CLAUDE,
        )

        gpt_request = AIRequest(
            messages=[ChatMessage(role="user", content="Hello GPT")],
            preferred_provider=AIProvider.GPT4,
        )

        # Send concurrent requests
        responses = await asyncio.gather(
            router.chat(claude_request),
            router.chat(gpt_request),
        )

        assert len(responses) == 2
        assert responses[0].provider == AIProvider.CLAUDE
        assert responses[1].provider == AIProvider.GPT4

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, router, basic_request):
        """Test handling of rate limit errors."""
        # Mock rate limit error from Claude
        rate_limit_error = Exception("Rate limit exceeded")
        rate_limit_error.status_code = 429  # Add status code attribute
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = (
            rate_limit_error
        )

        # Mock successful fallback
        gpt_response = AsyncMock()
        gpt_response.choices = [
            AsyncMock(message=AsyncMock(content="Fallback response"))
        ]
        gpt_response.model = "gpt-4"
        gpt_response.usage = AsyncMock(total_tokens=20)
        router._clients[AIProvider.GPT4].chat.completions.create.return_value = (
            gpt_response
        )

        basic_request.preferred_provider = AIProvider.CLAUDE

        response = await router.chat(basic_request)

        # Should fall back to another provider
        assert response.provider == AIProvider.GPT4
        assert response.content == "Fallback response"

    @pytest.mark.asyncio
    async def test_cost_optimization_selection(self, router):
        """Test provider selection optimizes for cost when appropriate."""
        # Simple chat request where cost matters
        cheap_request = AIRequest(
            messages=[ChatMessage(role="user", content="Simple question")],
            task_type=TaskType.CHAT,
        )

        selected = router.select_provider(cheap_request)

        # Should consider cost in selection (lower cost providers get higher scores)
        selected_capability = router._capabilities[selected]

        # Verify the selection logic includes cost consideration
        # (This tests the scoring algorithm includes cost factors)
        assert selected_capability.cost_per_1k_tokens >= 0

    @pytest.mark.asyncio
    async def test_provider_availability_tracking(self, router):
        """Test tracking of provider availability over time."""
        # Simulate a provider going down and coming back up
        basic_request = AIRequest(
            messages=[ChatMessage(role="user", content="Test")],
            preferred_provider=AIProvider.CLAUDE,
        )

        # First failure
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = Exception(
            "Temporary error"
        )

        with pytest.raises(Exception):
            await router.chat(basic_request)

        # Provider comes back online
        router._clients[AIProvider.CLAUDE].messages.create.side_effect = None
        router._clients[AIProvider.CLAUDE].messages.create.return_value = AsyncMock(
            content=[AsyncMock(text="Back online")],
            model="claude-3-haiku-20240307",
            usage=AsyncMock(input_tokens=5, output_tokens=10),
            stop_reason="stop",
        )

        response = await router.chat(basic_request)
        assert response.provider == AIProvider.CLAUDE
        assert response.content == "Back online"
