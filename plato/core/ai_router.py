"""AI Router for intelligent model selection and request routing."""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import anthropic
import google.generativeai as genai
import openai
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """Available AI providers."""

    CLAUDE = "claude"
    GPT4 = "gpt-4"
    GPT3_5 = "gpt-3.5-turbo"
    QWEN_LOCAL = "qwen-local"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"


class TaskType(str, Enum):
    """Task types for intelligent routing."""

    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    CHAT = "chat"
    REASONING = "reasoning"
    CREATIVE = "creative"
    TOOL_USE = "tool_use"


@dataclass
class AICapability:
    """Represents AI model capabilities."""

    provider: AIProvider
    strengths: list[TaskType] = field(default_factory=list)
    max_tokens: int = 4096
    supports_tools: bool = False
    supports_streaming: bool = True
    cost_per_1k_tokens: float = 0.0
    speed_rating: int = 5  # 1-10 scale
    quality_rating: int = 5  # 1-10 scale


class ChatMessage(BaseModel):
    """Standard chat message format."""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    name: str | None = Field(None, description="Optional sender name")
    tool_calls: list[dict[str, Any]] | None = Field(None, description="Tool calls")
    tool_call_id: str | None = Field(
        None, description="Tool call ID for tool responses"
    )


class AIRequest(BaseModel):
    """AI request with routing metadata."""

    messages: list[ChatMessage] = Field(..., description="Conversation messages")
    task_type: TaskType = Field(TaskType.CHAT, description="Type of task")
    preferred_provider: AIProvider | None = Field(
        None, description="Preferred AI provider"
    )
    max_tokens: int | None = Field(None, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Generation temperature")
    stream: bool = Field(False, description="Stream the response")
    tools: list[dict[str, Any]] | None = Field(None, description="Available tools")
    context: dict[str, Any] | None = Field(None, description="Additional context")


class AIResponse(BaseModel):
    """AI response with metadata."""

    content: str = Field(..., description="Generated content")
    provider: AIProvider = Field(..., description="Provider that generated response")
    model: str = Field(..., description="Specific model used")
    tokens_used: int = Field(0, description="Tokens consumed")
    finish_reason: str = Field("stop", description="Why generation stopped")
    tool_calls: list[dict[str, Any]] | None = Field(None, description="Tool calls made")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class AIRouter:
    """Intelligent AI router with capability-based model selection."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the AI router with configuration."""
        self.config = config or {}
        self._capabilities = self._init_capabilities()
        self._clients = {}
        self._rate_limits = {}
        self._initialized = False

        # Note: Client initialization moved to _ensure_initialized() for proper async handling

    def _init_capabilities(self) -> dict[AIProvider, AICapability]:
        """Initialize AI provider capabilities."""
        return {
            AIProvider.CLAUDE: AICapability(
                provider=AIProvider.CLAUDE,
                strengths=[
                    TaskType.CODE_ANALYSIS,
                    TaskType.REASONING,
                    TaskType.TOOL_USE,
                    TaskType.DOCUMENTATION,
                ],
                max_tokens=100000,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.015,
                speed_rating=7,
                quality_rating=9,
            ),
            AIProvider.GPT4: AICapability(
                provider=AIProvider.GPT4,
                strengths=[
                    TaskType.CODE_GENERATION,
                    TaskType.REASONING,
                    TaskType.TOOL_USE,
                    TaskType.CHAT,
                ],
                max_tokens=128000,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.03,
                speed_rating=6,
                quality_rating=9,
            ),
            AIProvider.GPT3_5: AICapability(
                provider=AIProvider.GPT3_5,
                strengths=[
                    TaskType.CHAT,
                    TaskType.CODE_GENERATION,
                    TaskType.DOCUMENTATION,
                ],
                max_tokens=16000,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.002,
                speed_rating=9,
                quality_rating=7,
            ),
            AIProvider.QWEN_LOCAL: AICapability(
                provider=AIProvider.QWEN_LOCAL,
                strengths=[TaskType.CODE_GENERATION, TaskType.CHAT, TaskType.CREATIVE],
                max_tokens=32000,
                supports_tools=True,  # Qwen local server supports OpenAI-compatible tools
                supports_streaming=True,
                cost_per_1k_tokens=0.0,  # Local model
                speed_rating=8,
                quality_rating=7,
            ),
            AIProvider.GEMINI: AICapability(
                provider=AIProvider.GEMINI,
                strengths=[
                    TaskType.CODE_ANALYSIS,
                    TaskType.REASONING,
                    TaskType.CREATIVE,
                ],
                max_tokens=30000,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.001,
                speed_rating=8,
                quality_rating=8,
            ),
            AIProvider.OPENROUTER: AICapability(
                provider=AIProvider.OPENROUTER,
                strengths=[TaskType.CODE_GENERATION, TaskType.CREATIVE, TaskType.CHAT],
                max_tokens=32000,
                supports_tools=True,
                supports_streaming=True,
                cost_per_1k_tokens=0.005,
                speed_rating=7,
                quality_rating=8,
            ),
        }

    async def _init_clients(self):
        """Initialize AI provider clients."""
        # Anthropic Claude
        if anthropic_key := self.config.get("anthropic_api_key"):
            self._clients[AIProvider.CLAUDE] = anthropic.AsyncAnthropic(
                api_key=anthropic_key
            )

        # OpenAI GPT models
        if openai_key := self.config.get("openai_api_key"):
            self._clients[AIProvider.GPT4] = openai.AsyncOpenAI(api_key=openai_key)
            self._clients[AIProvider.GPT3_5] = self._clients[AIProvider.GPT4]

        # Local Qwen - try multiple common endpoints
        qwen_url = self.config.get("qwen_base_url", "http://192.168.1.28:8000")
        try:
            # First try with /v1 endpoint (Ollama format)
            # Use much longer timeout for local Qwen model (120 seconds)
            self._clients[AIProvider.QWEN_LOCAL] = openai.AsyncOpenAI(
                base_url=f"{qwen_url}/v1",
                api_key="dummy-key",  # Local server doesn't need real key
                timeout=120.0,  # Increased from 10s to 120s for large local model
            )
            logger.info(
                f"Qwen local configured with base URL: {qwen_url}/v1 (timeout: 120s)"
            )
        except Exception as e:
            logger.warning(f"Failed to configure Qwen with /v1 endpoint: {e}")
            try:
                # Try without /v1 endpoint (direct OpenAI-compatible server)
                # Use much longer timeout for local Qwen model (120 seconds)
                self._clients[AIProvider.QWEN_LOCAL] = openai.AsyncOpenAI(
                    base_url=qwen_url,
                    api_key="dummy-key",
                    timeout=120.0,  # Increased from 10s to 120s for large local model
                )
                logger.info(
                    f"Qwen local configured with base URL: {qwen_url} (timeout: 120s)"
                )
            except Exception as e2:
                logger.error(f"Failed to configure Qwen local server: {e2}")

        # OpenRouter
        if openrouter_key := self.config.get("openrouter_api_key"):
            self._clients[AIProvider.OPENROUTER] = openai.AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=openrouter_key
            )

        # Google Gemini
        if gemini_key := self.config.get("gemini_api_key"):
            genai.configure(api_key=gemini_key)
            self._clients[AIProvider.GEMINI] = genai

    def select_provider(self, request: AIRequest) -> AIProvider:
        """Select the best AI provider for the request."""
        # Use preferred provider if specified and available
        if request.preferred_provider and request.preferred_provider in self._clients:
            return request.preferred_provider

        # Score available providers based on task type and capabilities
        scores = {}
        for provider, capability in self._capabilities.items():
            if provider not in self._clients:
                continue

            score = 0

            # Task type match
            if request.task_type in capability.strengths:
                score += 10

            # Tool support requirement
            if request.tools and capability.supports_tools:
                score += 5
            elif request.tools and not capability.supports_tools:
                score -= 10

            # Streaming requirement
            if request.stream and not capability.supports_streaming:
                score -= 5

            # Token limit consideration
            estimated_tokens = sum(len(msg.content) for msg in request.messages) // 4
            if request.max_tokens:
                estimated_tokens += request.max_tokens

            if estimated_tokens > capability.max_tokens:
                score -= 20

            # Quality and speed weights
            score += capability.quality_rating * 2
            score += capability.speed_rating

            # Cost consideration (lower cost = higher score)
            if capability.cost_per_1k_tokens > 0:
                score += max(0, 10 - capability.cost_per_1k_tokens * 1000)
            else:
                score += 15  # Free local models get bonus

            scores[provider] = score

        # Return provider with highest score
        if not scores:
            raise ValueError("No available AI providers configured")

        best_provider = max(scores.items(), key=lambda x: x[1])[0]
        logger.info(
            f"Selected provider: {best_provider} (score: {scores[best_provider]})"
        )
        return best_provider

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _ensure_initialized(self):
        """Ensure clients are initialized before use."""
        if not self._initialized:
            await self._init_clients()
            self._initialized = True

    async def chat(self, request: AIRequest) -> AIResponse:
        """Send chat request to selected AI provider."""
        await self._ensure_initialized()
        provider = self.select_provider(request)

        try:
            if provider == AIProvider.CLAUDE:
                return await self._chat_claude(request)
            elif provider in [
                AIProvider.GPT4,
                AIProvider.GPT3_5,
                AIProvider.QWEN_LOCAL,
                AIProvider.OPENROUTER,
            ]:
                return await self._chat_openai_compatible(request, provider)
            elif provider == AIProvider.GEMINI:
                return await self._chat_gemini(request)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"Error with provider {provider}: {e}")
            # Try fallback provider
            available_providers = [p for p in self._clients.keys() if p != provider]
            if available_providers:
                logger.info(f"Trying fallback provider: {available_providers[0]}")
                request.preferred_provider = available_providers[0]
                return await self.chat(request)
            raise

    async def _chat_claude(self, request: AIRequest) -> AIResponse:
        """Chat with Claude."""
        client = self._clients[AIProvider.CLAUDE]

        # Convert messages to Claude format
        claude_messages = []
        system_message = None

        for msg in request.messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                claude_messages.append({"role": msg.role, "content": msg.content})

        # Prepare request parameters
        params = {
            "model": "claude-3-haiku-20240307",  # Default model
            "messages": claude_messages,
            "max_tokens": request.max_tokens or 4096,
            "temperature": request.temperature,
            "stream": request.stream,
        }

        if system_message:
            params["system"] = system_message

        if request.tools:
            params["tools"] = request.tools

        if request.stream:
            return await self._stream_claude(client, params)
        else:
            response = await client.messages.create(**params)
            return AIResponse(
                content=response.content[0].text if response.content else "",
                provider=AIProvider.CLAUDE,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                finish_reason=response.stop_reason,
                tool_calls=getattr(response, "tool_calls", None),
                metadata={"usage": response.usage.model_dump()},
            )

    async def _chat_openai_compatible(
        self, request: AIRequest, provider: AIProvider
    ) -> AIResponse:
        """Chat with OpenAI-compatible APIs."""
        client = self._clients[provider]

        # Model mapping
        model_map = {
            AIProvider.GPT4: "gpt-4-turbo-preview",
            AIProvider.GPT3_5: "gpt-3.5-turbo",
            AIProvider.QWEN_LOCAL: "/opt/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",  # Actual model name from server
            AIProvider.OPENROUTER: "qwen/qwen3-coder:free",  # Use Qwen free model on OpenRouter
        }

        # Convert messages to OpenAI format
        openai_messages = [
            {
                "role": msg.role,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
            }
            for msg in request.messages
        ]

        # Prepare request parameters
        params = {
            "model": model_map[provider],
            "messages": openai_messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": request.stream,
        }

        if request.tools:
            params["tools"] = request.tools

        if request.stream:
            return await self._stream_openai_compatible(client, params, provider)
        else:
            response = await client.chat.completions.create(**params)
            choice = response.choices[0]
            return AIResponse(
                content=choice.message.content or "",
                provider=provider,
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                finish_reason=choice.finish_reason,
                tool_calls=getattr(choice.message, "tool_calls", None),
                metadata={
                    "usage": response.usage.model_dump() if response.usage else {}
                },
            )

    async def _chat_gemini(self, request: AIRequest) -> AIResponse:
        """Chat with Google Gemini."""
        import google.generativeai as genai

        model = genai.GenerativeModel("gemini-1.5-flash")

        # Convert messages to Gemini format
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"Human: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        prompt = "\n\n".join(prompt_parts)

        # Generate response
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens or 2048,
            ),
        )

        return AIResponse(
            content=response.text,
            provider=AIProvider.GEMINI,
            model="gemini-pro",
            tokens_used=0,  # Gemini doesn't provide token usage
            finish_reason="stop",
            metadata={"prompt_feedback": str(response.prompt_feedback)},
        )

    async def _stream_claude(self, client, params) -> AIResponse:
        """Stream response from Claude."""
        content_chunks = []
        tokens_used = 0

        async with client.messages.stream(**params) as stream:
            async for chunk in stream:
                if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                    content_chunks.append(chunk.delta.text)
                elif hasattr(chunk, "usage"):
                    tokens_used = chunk.usage.input_tokens + chunk.usage.output_tokens

        return AIResponse(
            content="".join(content_chunks),
            provider=AIProvider.CLAUDE,
            model=params["model"],
            tokens_used=tokens_used,
            finish_reason="stop",
        )

    async def _stream_openai_compatible(
        self, client, params, provider: AIProvider
    ) -> AIResponse:
        """Stream response from OpenAI-compatible API."""
        content_chunks = []
        finish_reason = "stop"

        async for chunk in await client.chat.completions.create(**params):
            if chunk.choices and chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)
            if chunk.choices and chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

        return AIResponse(
            content="".join(content_chunks),
            provider=provider,
            model=params["model"],
            tokens_used=0,  # Streaming doesn't provide token count
            finish_reason=finish_reason,
        )

    async def get_available_providers(self) -> list[AIProvider]:
        """Get list of available AI providers."""
        return list(self._clients.keys())

    def get_provider_capabilities(self, provider: AIProvider) -> AICapability | None:
        """Get capabilities for a specific provider."""
        return self._capabilities.get(provider)

    async def health_check(self) -> dict[str, bool]:
        """Check health of all AI providers."""
        await self._ensure_initialized()
        health = {}

        for provider in self._clients:
            try:
                # Send a simple test request
                test_request = AIRequest(
                    messages=[ChatMessage(role="user", content="Hello")],
                    max_tokens=10,
                    preferred_provider=provider,
                )
                await self.chat(test_request)
                health[provider.value] = True
            except Exception as e:
                logger.warning(f"Health check failed for {provider}: {e}")
                health[provider.value] = False

        return health
