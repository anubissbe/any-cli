#!/usr/bin/env python3
"""Basic usage examples for the Plato system."""

import asyncio
import json
from pathlib import Path

from plato.core.ai_router import AIRouter, AIRequest, TaskType, AIProvider
from plato.core.context_manager import ContextManager, ConversationMessage
from plato.core.mcp_manager import MCPManager, MCPServerConfig, MCPTransport
from plato.integrations.serena_mcp import SerenaMCPClient, SerenaLanguage


async def basic_ai_routing():
    """Demonstrate basic AI routing capabilities."""
    print("=== Basic AI Routing ===")

    # Initialize AI router with configuration
    config = {
        "anthropic_api_key": "your-api-key-here",
        "openai_api_key": "your-api-key-here",
        "qwen_base_url": "http://localhost:8000",
    }

    router = AIRouter(config)

    # Create a request
    request = AIRequest(
        messages=[
            {
                "role": "user",
                "content": "Explain the difference between async and sync programming",
            }
        ],
        task_type=TaskType.REASONING,
        max_tokens=500,
    )

    # Get response (router will automatically select best provider)
    try:
        response = await router.chat(request)
        print(f"Selected provider: {response.provider}")
        print(f"Response: {response.content[:200]}...")
        print(f"Tokens used: {response.tokens_used}")
    except Exception as e:
        print(f"Error: {e}")


async def context_management():
    """Demonstrate context management."""
    print("\n=== Context Management ===")

    context_manager = ContextManager()

    # Create a session
    session_id = await context_manager.create_session()
    print(f"Created session: {session_id}")

    # Add conversation messages
    await context_manager.add_message(
        ConversationMessage(
            role="user", content="Hello, I'm working on a Python project"
        ),
        session_id,
    )

    await context_manager.add_message(
        ConversationMessage(
            role="assistant",
            content="Great! I'd be happy to help with your Python project. What are you working on?",
        ),
        session_id,
    )

    # Add project context
    await context_manager.set_project_context(
        {
            "project_path": "/opt/projects/my-project",
            "language": "python",
            "framework": "fastapi",
        },
        session_id,
    )

    # Get conversation history
    history = context_manager.get_conversation_history(session_id)
    print(f"Conversation has {len(history)} messages")

    # Get context summary
    summary = context_manager.get_current_context_summary(session_id)
    print(f"Context summary: {json.dumps(summary, indent=2)}")


async def mcp_integration():
    """Demonstrate MCP server integration."""
    print("\n=== MCP Integration ===")

    mcp_manager = MCPManager()

    # Add Serena MCP server
    serena_config = MCPServerConfig(
        name="serena",
        transport=MCPTransport.SSE,
        url="http://localhost:8765",
        enabled=True,
    )
    mcp_manager.add_server(serena_config)

    # Connect to servers
    results = await mcp_manager.connect_all()
    print(f"Connection results: {results}")

    # List available tools
    tools = mcp_manager.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # Call a tool (if Serena is running)
    try:
        result = await mcp_manager.call_tool(
            "get_project_info", {"project_path": "/opt/projects"}
        )
        print(f"Tool result: {result}")
    except Exception as e:
        print(f"Tool call failed: {e}")

    await mcp_manager.disconnect_all()


async def serena_lsp_operations():
    """Demonstrate Serena LSP operations."""
    print("\n=== Serena LSP Operations ===")

    serena = SerenaMCPClient()

    # Connect to Serena
    connected = await serena.connect()
    if not connected:
        print("Failed to connect to Serena MCP server")
        return

    print("Connected to Serena MCP server")

    # Open a project
    project_path = "/opt/projects"
    result = await serena.open_project(project_path)
    if result.success:
        print(f"Opened project: {project_path}")

    # Find symbols
    symbols_result = await serena.find_symbols(
        project_path, "function", SerenaLanguage.PYTHON
    )
    if symbols_result.success:
        print(f"Found symbols: {len(symbols_result.data.get('symbols', []))}")

    # Build project context
    context = await serena.build_project_context(project_path)
    print(f"Project context keys: {list(context.keys())}")

    await serena.disconnect()


async def end_to_end_example():
    """Complete end-to-end example combining all components."""
    print("\n=== End-to-End Example ===")

    # Initialize all components
    ai_router = AIRouter()
    context_manager = ContextManager()
    serena_client = SerenaMCPClient()

    # Create session
    session_id = await context_manager.create_session(
        metadata={"example": "end-to-end", "project": "plato-demo"}
    )

    # Connect to Serena (if available)
    serena_connected = await serena_client.connect()

    # Simulate a conversation about code analysis
    user_message = ConversationMessage(
        role="user",
        content="I want to analyze a Python project for code quality issues",
    )
    await context_manager.add_message(user_message, session_id)

    # Get AI response
    history = context_manager.get_conversation_history(session_id)
    ai_request = AIRequest(
        messages=[{"role": msg.role, "content": msg.content} for msg in history],
        task_type=TaskType.CODE_ANALYSIS,
        max_tokens=300,
    )

    try:
        ai_response = await ai_router.chat(ai_request)

        # Add AI response to context
        ai_message = ConversationMessage(
            role="assistant",
            content=ai_response.content,
            ai_provider=ai_response.provider.value,
            tokens=ai_response.tokens_used,
        )
        await context_manager.add_message(ai_message, session_id)

        print(f"AI Response ({ai_response.provider}): {ai_response.content[:200]}...")

        # If Serena is connected, get actual project analysis
        if serena_connected:
            analysis = await serena_client.analyze_code_quality("/opt/projects/plato")
            if analysis.success:
                await context_manager.add_context(
                    content=f"Code analysis results: {json.dumps(analysis.data)}",
                    context_type="tool_result",
                    session_id=session_id,
                )
                print("Added code analysis to context")

    except Exception as e:
        print(f"Error in end-to-end example: {e}")

    finally:
        await serena_client.disconnect()

    # Show final context summary
    summary = context_manager.get_current_context_summary(session_id)
    print(f"Final context: {json.dumps(summary, indent=2)}")


async def main():
    """Run all examples."""
    print("Plato System Examples")
    print("====================")

    await basic_ai_routing()
    await context_management()
    await mcp_integration()
    await serena_lsp_operations()
    await end_to_end_example()

    print("\nExamples completed!")


if __name__ == "__main__":
    asyncio.run(main())
