#!/usr/bin/env python3
"""Demo script for the Plato Interactive CLI."""

import asyncio
import sys
from pathlib import Path

# Add the plato package to the Python path
plato_dir = Path(__file__).parent
sys.path.insert(0, str(plato_dir))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def show_demo_info():
    """Show information about the interactive CLI demo."""
    demo_info = """
# Plato Interactive CLI Demo

## Features Demonstrated

🚀 **Claude Code-like Interface**
- Rich terminal UI with syntax highlighting
- Interactive project navigation
- Context-aware conversations
- File tree exploration

🤖 **Multi-AI Integration**
- Automatic provider selection based on task type
- Support for Claude, GPT-4, Gemini, and local models
- Intelligent routing for optimal performance

🔧 **Tool Integration**
- Serena MCP for code analysis
- File operations and project management
- Git integration and project detection
- Real-time context building

## Commands Available

**Basic Chat:**
- Natural language conversations
- Automatic context awareness
- Multi-provider AI routing

**Project Navigation:**
- `/project` - Show project information
- `/files` - Toggle file tree display
- `/read <path>` - Read and display files
- `/search <pattern>` - Search project files

**Analysis & Tools:**
- `/analyze <path>` - Analyze files with LSP
- `/tools` - List available MCP tools
- `/provider <name>` - Set AI provider

**System Commands:**
- `/help` - Show all commands
- `/debug` - Toggle debug mode
- `/clear` - Clear conversation
- `/quit` - Exit

## Getting Started

1. **Start the Plato server:**
   ```bash
   python -m plato.server.api
   ```

2. **Launch interactive mode:**
   ```bash
   python -m plato.cli interactive
   # or
   python plato_interactive.py
   ```

3. **Try natural language commands:**
   - "Show me the project structure"
   - "Find all Python files"
   - "Analyze the main module"
   - "Help me refactor this function"

## Example Session

```
You: Show me the project structure
🤖 CLAUDE: I'll analyze your project structure...
[Project tree and analysis displayed]

You: /read plato/cli.py
[File content with syntax highlighting]

You: Help me add error handling to this function
🤖 CLAUDE: I can help improve error handling...
[Code suggestions and improvements]
```

**Note:** Some features require Serena MCP server running for full functionality.
    """

    panel = Panel(
        Markdown(demo_info),
        title="[bold blue]Plato Interactive CLI Demo[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)


def main():
    """Main demo function."""
    show_demo_info()

    choice = console.input(
        "\n[cyan]Would you like to start the interactive CLI? (y/n): [/cyan]"
    )

    if choice.lower() in ["y", "yes"]:
        console.print("\n[green]Starting Plato Interactive CLI...[/green]")

        # Import and run the interactive CLI
        from plato.interactive_cli import main as interactive_main

        asyncio.run(interactive_main())
    else:
        console.print(
            "\n[yellow]Demo complete. Use 'python -m plato.cli interactive' to start later.[/yellow]"
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo cancelled.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]")
