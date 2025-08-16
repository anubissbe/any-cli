#!/usr/bin/env python3
"""Demo script showing embedded tools with AI interaction."""

import asyncio
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from plato.core.embedded_tools import ToolManager


console = Console()


async def demo_ai_tool_use():
    """Demonstrate how AI can use embedded tools."""
    console.print("[bold cyan]🤖 Plato Embedded Tools Demo[/bold cyan]\n")

    tool_manager = ToolManager()

    # Simulated AI requests (in real usage, these would come from the AI)
    ai_requests = [
        {
            "description": "Creating a Python project structure",
            "tools": [
                {
                    "tool": "CreateDirectoryTool",
                    "parameters": {"directory_path": "/tmp/demo_project"},
                },
                {
                    "tool": "CreateDirectoryTool",
                    "parameters": {"directory_path": "/tmp/demo_project/src"},
                },
                {
                    "tool": "CreateDirectoryTool",
                    "parameters": {"directory_path": "/tmp/demo_project/tests"},
                },
            ],
        },
        {
            "description": "Writing project files",
            "tools": [
                {
                    "tool": "WriteFileTool",
                    "parameters": {
                        "file_path": "/tmp/demo_project/README.md",
                        "content": """# Demo Project

This is a demo project created by Plato's embedded tools.

## Features
- Automated file operations
- Claude Code-like functionality
- No external MCP servers required

## Structure
```
demo_project/
├── src/
│   └── main.py
├── tests/
│   └── test_main.py
└── README.md
```
""",
                    },
                },
                {
                    "tool": "WriteFileTool",
                    "parameters": {
                        "file_path": "/tmp/demo_project/src/main.py",
                        "content": '''"""Main module for demo project."""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to Plato."


def main():
    """Main entry point."""
    print(greet("User"))
    print("This project was created using Plato's embedded tools!")


if __name__ == "__main__":
    main()
''',
                    },
                },
                {
                    "tool": "WriteFileTool",
                    "parameters": {
                        "file_path": "/tmp/demo_project/tests/test_main.py",
                        "content": '''"""Tests for main module."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import greet


def test_greet():
    """Test the greet function."""
    assert greet("Alice") == "Hello, Alice! Welcome to Plato."
    assert greet("Bob") == "Hello, Bob! Welcome to Plato."
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_greet()
''',
                    },
                },
            ],
        },
        {
            "description": "Verifying project structure",
            "tools": [
                {
                    "tool": "ListDirectoryTool",
                    "parameters": {
                        "directory_path": "/tmp/demo_project",
                        "recursive": True,
                        "max_depth": 2,
                    },
                }
            ],
        },
        {
            "description": "Reading and displaying main.py",
            "tools": [
                {
                    "tool": "ReadFileTool",
                    "parameters": {
                        "file_path": "/tmp/demo_project/src/main.py",
                        "start_line": 1,
                        "end_line": 10,
                    },
                }
            ],
        },
    ]

    # Execute AI requests
    for request_group in ai_requests:
        console.print(f"\n[bold green]📋 {request_group['description']}[/bold green]")
        console.print("-" * 50)

        for tool_request in request_group["tools"]:
            tool_name = tool_request["tool"]
            parameters = tool_request["parameters"]

            console.print(f"\n[cyan]Executing:[/cyan] {tool_name}")
            if "file_path" in parameters or "directory_path" in parameters:
                path = parameters.get("file_path") or parameters.get("directory_path")
                console.print(f"[dim]Path: {path}[/dim]")

            try:
                result = await tool_manager.execute_tool(tool_name, **parameters)

                if result.success:
                    console.print("[green]✅ Success[/green]")
                    if result.data and tool_name in [
                        "ReadFileTool",
                        "ListDirectoryTool",
                    ]:
                        # Display file content or directory listing
                        if isinstance(result.data, str):
                            if len(result.data) > 500:
                                # Truncate long output
                                display_data = result.data[:500] + "\n... (truncated)"
                            else:
                                display_data = result.data
                            console.print(
                                Panel(display_data, title="Output", border_style="blue")
                            )
                else:
                    console.print(f"[red]❌ Failed: {result.error}[/red]")

            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")

        await asyncio.sleep(0.5)  # Small delay for demo effect

    console.print("\n" + "=" * 60)
    console.print("\n[bold green]✨ Demo Complete![/bold green]")
    console.print("\nThe AI has successfully:")
    console.print("1. Created a Python project structure")
    console.print("2. Written multiple source files")
    console.print("3. Verified the directory structure")
    console.print("4. Read and displayed file contents")
    console.print(
        "\n[dim]All operations were performed using embedded tools, no external MCP servers required![/dim]"
    )


async def interactive_demo():
    """Interactive demo where user can request tool operations."""
    console.print("[bold cyan]🤖 Plato Interactive Tool Demo[/bold cyan]\n")
    console.print("Type tool requests in natural language or JSON format.")
    console.print("Examples:")
    console.print('  - "read file /tmp/demo_project/README.md"')
    console.print(
        '  - {"tool": "ListDirectoryTool", "parameters": {"directory_path": "/tmp"}}'
    )
    console.print("\nType 'quit' to exit.\n")

    tool_manager = ToolManager()

    while True:
        try:
            user_input = input("[You] > ").strip()

            if user_input.lower() == "quit":
                break

            # Try to parse and execute
            result = await tool_manager.execute_from_text(user_input)

            if result:
                output = tool_manager.format_tool_result(result)
                console.print(
                    Panel(output, title="[bold green]Tool Result[/bold green]")
                )
            else:
                # Try JSON parsing
                try:
                    request = json.loads(user_input)
                    if "tool" in request:
                        tool_name = request["tool"]
                        parameters = request.get("parameters", {})
                        result = await tool_manager.execute_tool(
                            tool_name, **parameters
                        )
                        output = tool_manager.format_tool_result(result)
                        console.print(
                            Panel(output, title="[bold green]Tool Result[/bold green]")
                        )
                    else:
                        console.print(
                            "[yellow]Could not parse request. Use natural language or JSON format.[/yellow]"
                        )
                except json.JSONDecodeError:
                    console.print(
                        "[yellow]Could not parse request. Try a simpler format.[/yellow]"
                    )

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    console.print("\n[dim]Goodbye![/dim]")


async def main():
    """Main entry point."""
    console.print("Choose demo mode:")
    console.print("1. Automated AI demo (shows how AI uses tools)")
    console.print("2. Interactive mode (you control the tools)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        await demo_ai_tool_use()
    elif choice == "2":
        await interactive_demo()
    else:
        console.print("[red]Invalid choice[/red]")


if __name__ == "__main__":
    asyncio.run(main())
