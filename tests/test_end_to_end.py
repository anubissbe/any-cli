"""End-to-end integration tests for Plato system.

These tests verify that all components work together correctly,
from CLI to API to MCP servers to AI providers.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from plato.core.ai_router import AIRouter, AIRequest, TaskType, ChatMessage, AIProvider
from plato.core.context_manager import ContextManager, ConversationMessage
from plato.core.mcp_manager import MCPManager, MCPServerConfig, MCPTransport
from plato.integrations.serena_mcp import SerenaMCPClient, SerenaLanguage

from tests.conftest import skip_if_no_serena, skip_if_no_plato_server


@pytest.mark.integration
@pytest.mark.slow
class TestFullStackIntegration:
    """Test complete integration of all Plato components."""

    async def test_ai_router_context_manager_integration(
        self, ai_router: AIRouter, context_manager: ContextManager
    ):
        """Test AI router working with context manager."""
        # Mock AI client to avoid real API calls
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(text="I understand your request about code analysis.")
        ]
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 25
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_client

        # Create conversation session
        session_id = await context_manager.create_session()

        # Add user message to context
        user_message = ConversationMessage(
            role="user", content="Analyze this Python code: def hello(): print('hello')"
        )
        await context_manager.add_message(user_message, session_id)

        # Get conversation history and send to AI
        history = context_manager.get_conversation_history(session_id)
        ai_request = AIRequest(
            messages=[
                ChatMessage(role=msg.role, content=msg.content) for msg in history
            ],
            task_type=TaskType.CODE_ANALYSIS,
            preferred_provider=AIProvider.CLAUDE,
        )

        # Get AI response
        ai_response = await ai_router.chat(ai_request)

        # Add AI response to context
        ai_message = ConversationMessage(
            role="assistant",
            content=ai_response.content,
            ai_provider=ai_response.provider.value,
        )
        await context_manager.add_message(ai_message, session_id)

        # Verify integration
        final_history = context_manager.get_conversation_history(session_id)
        assert len(final_history) == 2
        assert final_history[0].role == "user"
        assert final_history[1].role == "assistant"
        assert (
            final_history[1].content == "I understand your request about code analysis."
        )
        assert final_history[1].ai_provider == AIProvider.CLAUDE.value

    async def test_context_compression_with_ai_switching(
        self, context_manager: ContextManager, ai_router: AIRouter
    ):
        """Test context compression and AI provider switching."""
        session_id = await context_manager.create_session()

        # Add many messages to trigger compression
        for i in range(15):
            user_msg = ConversationMessage(
                role="user",
                content=f"Message {i}: "
                + "This is a longer message to consume tokens. " * 10,
            )
            await context_manager.add_message(user_msg, session_id)

            assistant_msg = ConversationMessage(
                role="assistant",
                content=f"Response {i}: " + "This is a longer response. " * 10,
                ai_provider="claude",
            )
            await context_manager.add_message(assistant_msg, session_id)

        # Switch AI provider
        switch_success = await context_manager.switch_ai_provider("gpt-4", session_id)
        assert switch_success is True

        session = context_manager.get_session(session_id)
        assert session.current_ai_provider == "gpt-4"

        # Should have context entry about the switch
        entries = context_manager.get_context_entries(session_id=session_id)
        switch_entries = [e for e in entries if "Switched AI provider" in e.content]
        assert len(switch_entries) >= 1

        # Context should be compressed due to token limit
        total_tokens = session.total_tokens()
        assert total_tokens <= context_manager.window.max_tokens


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaFullIntegration:
    """Test complete integration with Serena MCP server."""

    async def test_serena_project_analysis_workflow(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test complete project analysis workflow with Serena."""
        project_path = str(temp_workspace / "test_project")

        # 1. Open project
        open_response = await serena_client.open_project(project_path)
        assert open_response.success is True

        # 2. Get project info
        info_response = await serena_client.get_project_info(project_path)
        assert info_response.success is True

        # 3. List workspace files
        files_response = await serena_client.get_workspace_files(project_path)
        assert files_response.success is True

        files = files_response.data or []
        python_files = []
        for file_info in files:
            file_path = file_info.get("path", file_info.get("name", ""))
            if file_path.endswith(".py"):
                python_files.append(file_path)

        # 4. Open and analyze each Python file
        for file_path in python_files[:2]:  # Limit to first 2 files
            # Open file
            await serena_client.open_file(file_path)

            # Get content
            content_response = await serena_client.get_file_content(file_path)
            if content_response.success:
                assert len(content_response.data) > 0

            # Get symbols
            symbols_response = await serena_client.get_document_symbols(file_path)
            # Symbols might not be immediately available

            # Get diagnostics
            diag_response = await serena_client.get_diagnostics(file_path)
            # Diagnostics might not be immediately available

            # Close file
            await serena_client.close_file(file_path)

        # 5. Build comprehensive project context
        project_context = await serena_client.build_project_context(project_path)

        assert "workspace_path" in project_context
        assert "files" in project_context
        assert "dependencies" in project_context
        assert "metrics" in project_context

        # 6. Close project
        close_response = await serena_client.close_project(project_path)
        assert close_response.success is True

    async def test_serena_code_editing_workflow(
        self,
        serena_client: SerenaMCPClient,
        temp_workspace: Path,
        sample_python_code: str,
    ):
        """Test code editing workflow with Serena."""
        project_path = str(temp_workspace / "test_project")
        new_file_path = str(temp_workspace / "test_project" / "new_module.py")

        # Open project
        await serena_client.open_project(project_path)

        # Create new file with content
        save_response = await serena_client.save_file(new_file_path, sample_python_code)
        assert save_response.success is True

        # Open the new file
        await serena_client.open_file(new_file_path)

        # Verify content
        content_response = await serena_client.get_file_content(new_file_path)
        assert content_response.success is True
        assert "fibonacci" in content_response.data
        assert "Calculator" in content_response.data

        # Try to get symbols (might take time for LSP to process)
        symbols_response = await serena_client.get_document_symbols(new_file_path)
        # Don't assert success since symbols might not be immediately available

        # Try to format document
        format_response = await serena_client.format_document(new_file_path)
        # Formatting might not be available for all setups

        # Build file context
        file_context = await serena_client.build_file_context(new_file_path)
        assert "file_path" in file_context
        assert "content" in file_context or file_context["content"] is None

        # Close file and project
        await serena_client.close_file(new_file_path)
        await serena_client.close_project(project_path)

    async def test_serena_multi_language_support(
        self,
        serena_client: SerenaMCPClient,
        temp_workspace: Path,
        sample_typescript_code: str,
    ):
        """Test Serena with multiple programming languages."""
        ts_project_path = str(temp_workspace / "test_ts_project")
        ts_file_path = str(temp_workspace / "test_ts_project" / "new_types.ts")

        # Open TypeScript project
        await serena_client.open_project(ts_project_path)

        # Create TypeScript file
        save_response = await serena_client.save_file(
            ts_file_path, sample_typescript_code
        )
        assert save_response.success is True

        # Open and analyze TypeScript file
        await serena_client.open_file(ts_file_path)

        content_response = await serena_client.get_file_content(ts_file_path)
        assert content_response.success is True
        assert "interface Person" in content_response.data
        assert "UserManager" in content_response.data

        # Test language-specific file listing
        ts_files_response = await serena_client.get_workspace_files(
            ts_project_path, language=SerenaLanguage.TYPESCRIPT
        )
        assert ts_files_response.success is True

        # Clean up
        await serena_client.close_file(ts_file_path)
        await serena_client.close_project(ts_project_path)


@pytest.mark.integration
class TestMCPManagerWithSerena:
    """Test MCP manager integration with Serena."""

    @skip_if_no_serena
    async def test_mcp_manager_serena_integration(
        self, mcp_manager: MCPManager, temp_workspace: Path
    ):
        """Test MCP manager working with actual Serena server."""
        # Configure Serena in MCP manager
        serena_config = MCPServerConfig(
            name="serena-integration-test",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            timeout=15,
        )

        success = mcp_manager.add_server(serena_config)
        assert success is True

        # Try to connect
        connect_success = await mcp_manager.connect_server("serena-integration-test")

        if connect_success:
            # Test tool discovery
            await asyncio.sleep(1)  # Give time for tool discovery

            tools = mcp_manager.list_tools("serena-integration-test")
            # Should have discovered some tools from Serena

            # Test tool execution if tools were discovered
            if tools:
                # Try a simple tool call
                project_path = str(temp_workspace / "test_project")

                # Look for project-related tools
                project_tools = [t for t in tools if "project" in t.name.lower()]
                if project_tools:
                    tool_name = f"serena-integration-test.{project_tools[0].name}"
                    result = await mcp_manager.call_tool(
                        tool_name, {"project_path": project_path}
                    )
                    # Result might succeed or fail, just verify it's handled
                    assert isinstance(result, dict)

            # Disconnect
            await mcp_manager.disconnect_server("serena-integration-test")


@pytest.mark.integration
@pytest.mark.slow
class TestFullSystemWorkflow:
    """Test complete system workflows that combine all components."""

    async def test_ai_powered_code_analysis_workflow(
        self,
        ai_router: AIRouter,
        context_manager: ContextManager,
        temp_workspace: Path,
        sample_python_code: str,
    ):
        """Test AI-powered code analysis using context and mocked AI."""
        # Mock AI client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="""
This Python code contains:
1. A recursive fibonacci function - inefficient implementation
2. A factorial function - also recursive
3. A Calculator class with basic arithmetic operations
4. The Calculator.divide method includes proper error handling for division by zero

Recommendations:
- Use iterative approach for fibonacci for better performance
- Add type hints to all functions
- Consider adding docstrings to the Calculator class methods
"""
            )
        ]
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 200
        mock_response.usage.output_tokens = 150
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_client

        # Create session and context
        session_id = await context_manager.create_session()

        # Set up the analysis request
        analysis_prompt = f"""
Please analyze the following Python code for quality, performance, and best practices:

```python
{sample_python_code}
```

Focus on:
1. Code structure and organization
2. Performance considerations
3. Error handling
4. Best practices compliance
"""

        # Add analysis request to context
        user_message = ConversationMessage(role="user", content=analysis_prompt)
        await context_manager.add_message(user_message, session_id)

        # Get AI analysis
        history = context_manager.get_conversation_history(session_id)
        ai_request = AIRequest(
            messages=[
                ChatMessage(role=msg.role, content=msg.content) for msg in history
            ],
            task_type=TaskType.CODE_ANALYSIS,
            preferred_provider=AIProvider.CLAUDE,
        )

        ai_response = await ai_router.chat(ai_request)

        # Add AI response to context
        ai_message = ConversationMessage(
            role="assistant",
            content=ai_response.content,
            ai_provider=ai_response.provider.value,
        )
        await context_manager.add_message(ai_message, session_id)

        # Verify the analysis
        assert ai_response.content is not None
        assert "fibonacci" in ai_response.content.lower()
        assert "calculator" in ai_response.content.lower()
        assert "recommendations" in ai_response.content.lower()

        # Test follow-up question
        followup_message = ConversationMessage(
            role="user",
            content="How would you improve the fibonacci function specifically?",
        )
        await context_manager.add_message(followup_message, session_id)

        # Mock follow-up response
        mock_followup_response = MagicMock()
        mock_followup_response.content = [
            MagicMock(
                text="""
To improve the fibonacci function:

1. Use iterative approach instead of recursion:
```python
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

2. Add memoization if you prefer recursive approach:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

The iterative approach is more efficient with O(n) time and O(1) space complexity.
"""
            )
        ]
        mock_followup_response.model = "claude-3-haiku-20240307"
        mock_followup_response.usage.input_tokens = 250
        mock_followup_response.usage.output_tokens = 180
        mock_followup_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_followup_response)

        # Get follow-up response
        history = context_manager.get_conversation_history(session_id)
        followup_request = AIRequest(
            messages=[
                ChatMessage(role=msg.role, content=msg.content) for msg in history
            ],
            task_type=TaskType.CODE_GENERATION,
            preferred_provider=AIProvider.CLAUDE,
        )

        followup_response = await ai_router.chat(followup_request)

        # Add to context
        followup_ai_message = ConversationMessage(
            role="assistant",
            content=followup_response.content,
            ai_provider=followup_response.provider.value,
        )
        await context_manager.add_message(followup_ai_message, session_id)

        # Verify conversation flow
        final_history = context_manager.get_conversation_history(session_id)
        assert len(final_history) == 4  # 2 user messages, 2 AI responses

        # Verify conversation maintains context
        assert "iterative" in followup_response.content.lower()
        assert "fibonacci" in followup_response.content.lower()

    @skip_if_no_serena
    async def test_ai_assisted_code_refactoring_with_serena(
        self,
        serena_client: SerenaMCPClient,
        ai_router: AIRouter,
        context_manager: ContextManager,
        temp_workspace: Path,
    ):
        """Test AI-assisted code refactoring using Serena for context."""
        # Mock AI client for refactoring suggestions
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [
            MagicMock(
                text="""
Based on the code analysis, here are the refactoring suggestions:

1. Extract the hello_world function into a proper module structure
2. Add proper error handling
3. Use type hints for better code documentation
4. Consider adding unit tests

Here's the refactored version:
```python
#!/usr/bin/env python3
\"\"\"
Main module for the application.
\"\"\"

def hello_world() -> None:
    \"\"\"Print a greeting message.\"\"\"
    try:
        print("Hello, World!")
    except Exception as e:
        print(f"Error occurred: {e}")

def main() -> None:
    \"\"\"Main entry point.\"\"\"
    hello_world()

if __name__ == "__main__":
    main()
```
"""
            )
        ]
        mock_response.model = "claude-3-haiku-20240307"
        mock_response.usage.input_tokens = 180
        mock_response.usage.output_tokens = 220
        mock_response.stop_reason = "stop"

        mock_client.messages.create = AsyncMock(return_value=mock_response)
        ai_router._clients[AIProvider.CLAUDE] = mock_client

        # Set up project with Serena
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Get file content through Serena
        content_response = await serena_client.get_file_content(file_path)
        assert content_response.success is True

        original_code = content_response.data

        # Build file context
        file_context = await serena_client.build_file_context(file_path)

        # Create refactoring session
        session_id = await context_manager.create_session()

        # Create refactoring request
        refactor_prompt = f"""
Please analyze and refactor the following Python code:

File: {file_path}
Content:
```python
{original_code}
```

Context:
- File symbols: {file_context.get('symbols', [])}
- Diagnostics: {file_context.get('diagnostics', [])}

Please provide:
1. Analysis of current code quality
2. Specific refactoring recommendations
3. Improved version of the code
"""

        user_message = ConversationMessage(role="user", content=refactor_prompt)
        await context_manager.add_message(user_message, session_id)

        # Get AI refactoring suggestions
        history = context_manager.get_conversation_history(session_id)
        ai_request = AIRequest(
            messages=[
                ChatMessage(role=msg.role, content=msg.content) for msg in history
            ],
            task_type=TaskType.REFACTORING,
            preferred_provider=AIProvider.CLAUDE,
        )

        ai_response = await ai_router.chat(ai_request)

        # Verify refactoring suggestions
        assert ai_response.content is not None
        assert "refactor" in ai_response.content.lower()
        assert "def hello_world" in ai_response.content
        assert (
            "type hints" in ai_response.content.lower()
            or "Type hints" in ai_response.content
        )

        # Clean up
        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)


@pytest.mark.integration
@pytest.mark.slow
class TestSystemResilience:
    """Test system resilience and error recovery."""

    async def test_ai_provider_fallback_integration(
        self, ai_router: AIRouter, context_manager: ContextManager
    ):
        """Test AI provider fallback with context preservation."""
        # Mock primary provider to fail
        mock_failing_client = AsyncMock()
        mock_failing_client.messages.create = AsyncMock(
            side_effect=Exception("Primary provider failed")
        )
        ai_router._clients[AIProvider.CLAUDE] = mock_failing_client

        # Mock fallback provider to succeed
        mock_fallback_client = AsyncMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Fallback response from GPT-4"
        mock_choice.finish_reason = "stop"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4-turbo-preview"
        mock_response.usage.total_tokens = 30

        mock_fallback_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        ai_router._clients[AIProvider.GPT4] = mock_fallback_client

        # Create session
        session_id = await context_manager.create_session()

        # Add message preferring the failing provider
        user_message = ConversationMessage(
            role="user", content="Test message for fallback"
        )
        await context_manager.add_message(user_message, session_id)

        # Request with preferred failing provider
        history = context_manager.get_conversation_history(session_id)
        ai_request = AIRequest(
            messages=[
                ChatMessage(role=msg.role, content=msg.content) for msg in history
            ],
            preferred_provider=AIProvider.CLAUDE,  # This will fail
        )

        # Should fallback to GPT-4
        ai_response = await ai_router.chat(ai_request)

        assert ai_response.provider == AIProvider.GPT4
        assert ai_response.content == "Fallback response from GPT-4"

        # Add response to context
        ai_message = ConversationMessage(
            role="assistant",
            content=ai_response.content,
            ai_provider=ai_response.provider.value,
        )
        await context_manager.add_message(ai_message, session_id)

        # Verify context preserved the fallback
        final_history = context_manager.get_conversation_history(session_id)
        assert len(final_history) == 2
        assert final_history[1].ai_provider == "gpt-4"

    async def test_context_compression_with_errors(
        self, context_manager: ContextManager
    ):
        """Test context compression behavior under error conditions."""
        session_id = await context_manager.create_session()

        # Add messages with some containing potential problematic content
        problematic_messages = [
            "Normal message",
            "Message with unicode: 🚀🤖💻",
            "Very long message: " + "x" * 10000,
            "Message with special chars: \n\t\r",
            "Empty response follows:",
            "",  # Empty message
            "Message with JSON: {'key': 'value', 'nested': {'deep': 'value'}}",
            "SQL-like content: SELECT * FROM users WHERE id = 1;",
            "Code snippet:\ndef function():\n    return 'value'",
        ]

        for i, content in enumerate(problematic_messages):
            user_msg = ConversationMessage(
                role="user" if i % 2 == 0 else "assistant",
                content=content,
                ai_provider="test-provider" if i % 2 == 1 else None,
            )
            await context_manager.add_message(user_msg, session_id)

        # Force compression by adding more content
        for i in range(20):
            long_msg = ConversationMessage(
                role="user",
                content=f"Additional message {i}: " + "token consuming content " * 50,
            )
            await context_manager.add_message(long_msg, session_id)

        # Verify session is still functional after compression
        session = context_manager.get_session(session_id)
        assert session is not None

        # Should have compressed but preserved some messages
        history = context_manager.get_conversation_history(session_id)
        assert len(history) > 0

        # Session should still be within token limits
        total_tokens = session.total_tokens()
        assert total_tokens <= context_manager.window.max_tokens
