"""Interactive CLI for Plato - Claude Code-like interface."""

import asyncio
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from plato.core.ai_router import AIProvider, TaskType
from plato.core.embedded_tools import ToolManager, ToolResult

# Serena MCP removed - using embedded tools only
HAS_SERENA = False

# Optional imports for enhanced features
try:
    import git

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

try:
    from pygments.lexers import get_lexer_for_filename
    from pygments.util import ClassNotFound

    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


class ProjectContext:
    """Manages project context and detection."""

    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.project_type = None
        self.git_repo = None
        self.config_files = []
        self.language = None
        self._detect_project()

    def _detect_project(self):
        """Detect project type and context."""
        # Check for git repository
        if HAS_GIT:
            try:
                self.git_repo = git.Repo(self.path, search_parent_directories=True)
            except git.InvalidGitRepositoryError:
                pass

        # Detect project type based on files
        project_files = {
            "package.json": "node",
            "pyproject.toml": "python",
            "requirements.txt": "python",
            "Cargo.toml": "rust",
            "go.mod": "go",
            "composer.json": "php",
            "pom.xml": "java",
            "build.gradle": "java",
            "Gemfile": "ruby",
            "mix.exs": "elixir",
        }

        for file_name, project_type in project_files.items():
            if (self.path / file_name).exists():
                self.project_type = project_type
                self.config_files.append(file_name)
                break

        # Detect primary language
        language_extensions = {
            ".py": "python",
            ".ts": "typescript",
            ".js": "javascript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".php": "php",
            ".rb": "ruby",
            ".ex": "elixir",
            ".exs": "elixir",
        }

        # Count files by extension
        extension_counts = {}
        for file_path in self.path.rglob("*"):
            if file_path.is_file() and not any(
                part.startswith(".") for part in file_path.parts[len(self.path.parts) :]
            ):
                ext = file_path.suffix.lower()
                if ext in language_extensions:
                    extension_counts[ext] = extension_counts.get(ext, 0) + 1

        if extension_counts:
            most_common_ext = max(extension_counts, key=extension_counts.get)
            self.language = language_extensions[most_common_ext]

    def get_summary(self) -> Dict[str, Any]:
        """Get project summary."""
        summary = {
            "path": str(self.path),
            "name": self.path.name,
            "type": self.project_type or "unknown",
            "language": self.language or "unknown",
            "config_files": self.config_files,
        }

        if self.git_repo:
            try:
                summary["git"] = {
                    "branch": self.git_repo.active_branch.name,
                    "remote": (
                        str(self.git_repo.remotes.origin.url)
                        if self.git_repo.remotes
                        else None
                    ),
                    "dirty": self.git_repo.is_dirty(),
                    "commits": len(list(self.git_repo.iter_commits(max_count=10))),
                }
            except Exception:
                summary["git"] = {"error": "Could not read git info"}

        return summary


class FileExplorer:
    """File tree explorer for the interactive CLI."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.expanded_dirs = {self.root_path}
        self.current_file = None

    def build_tree(self, max_depth: int = 3) -> Tree:
        """Build a file tree representation."""
        tree = Tree(f"[bold blue]{self.root_path.name}[/bold blue]")
        self._add_directory_to_tree(tree, self.root_path, 0, max_depth)
        return tree

    def _add_directory_to_tree(
        self, parent_tree: Tree, directory: Path, depth: int, max_depth: int
    ):
        """Recursively add directory contents to tree."""
        if depth >= max_depth:
            return

        # Skip hidden directories and common ignore patterns
        ignore_patterns = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "target",
            "dist",
            "build",
        }

        try:
            entries = sorted(
                directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
            )
            dirs = [e for e in entries if e.is_dir() and e.name not in ignore_patterns]
            files = [e for e in entries if e.is_file() and not e.name.startswith(".")]

            # Add directories first
            for dir_path in dirs[:10]:  # Limit to first 10 to avoid clutter
                dir_node = parent_tree.add(f"[bold cyan]{dir_path.name}/[/bold cyan]")
                if dir_path in self.expanded_dirs:
                    self._add_directory_to_tree(
                        dir_node, dir_path, depth + 1, max_depth
                    )

            # Add files
            for file_path in files[:20]:  # Limit to first 20 files
                file_icon = self._get_file_icon(file_path)
                file_color = self._get_file_color(file_path)
                file_node = parent_tree.add(
                    f"{file_icon} [{file_color}]{file_path.name}[/{file_color}]"
                )

        except PermissionError:
            parent_tree.add("[red]Permission denied[/red]")

    def _get_file_icon(self, file_path: Path) -> str:
        """Get icon for file type."""
        ext = file_path.suffix.lower()
        icons = {
            ".py": "🐍",
            ".js": "🟨",
            ".ts": "🔷",
            ".html": "🌐",
            ".css": "🎨",
            ".json": "📋",
            ".md": "📝",
            ".yml": "⚙️",
            ".yaml": "⚙️",
            ".toml": "⚙️",
            ".go": "🐹",
            ".rs": "🦀",
            ".java": "☕",
            ".php": "🐘",
            ".rb": "💎",
        }
        return icons.get(ext, "📄")

    def _get_file_color(self, file_path: Path) -> str:
        """Get color for file type."""
        ext = file_path.suffix.lower()
        colors = {
            ".py": "bright_yellow",
            ".js": "yellow",
            ".ts": "blue",
            ".html": "orange3",
            ".css": "magenta",
            ".json": "cyan",
            ".md": "green",
            ".yml": "purple",
            ".yaml": "purple",
            ".toml": "purple",
            ".go": "cyan",
            ".rs": "red",
            ".java": "orange3",
            ".php": "purple",
            ".rb": "red",
        }
        return colors.get(ext, "white")


class SessionManager:
    """Manages chat sessions and context."""

    def __init__(self):
        self.session_id = None
        self.messages = []
        self.context = {}
        self.start_time = datetime.now()
        self.tokens_used = 0
        self.current_provider = None

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to session history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)

    def get_context_summary(self) -> str:
        """Get a summary of the current context."""
        duration = datetime.now() - self.start_time
        return (
            f"Session: {self.session_id or 'New'} | "
            f"Duration: {duration.total_seconds():.0f}s | "
            f"Messages: {len(self.messages)} | "
            f"Tokens: {self.tokens_used} | "
            f"Provider: {self.current_provider or 'Auto'}"
        )


class PlatoInteractiveCLI:
    """Interactive CLI interface for Plato."""

    def __init__(self, server_url: str = "http://localhost:8080"):
        self.console = Console()
        self.server_url = server_url
        self.client = httpx.AsyncClient(timeout=30.0)

        # Core components
        self.project_context = ProjectContext()
        self.file_explorer = FileExplorer()
        self.session_manager = SessionManager()
        self.serena_client = None
        self.tool_manager = ToolManager()  # Initialize embedded tools

        # State
        self.running = True
        self.show_file_tree = True
        self.auto_context = True
        self.debug_mode = False

        # Layout
        self.layout = Layout()
        self._setup_layout()

    def _setup_layout(self):
        """Setup the CLI layout."""
        # Create sub-layouts first
        header = Layout(name="header", size=3)
        footer = Layout(name="footer", size=3)

        # Create main layout with pre-split content
        sidebar = Layout(name="sidebar", size=40)
        content = Layout(name="content")
        main = Layout(name="main")
        main.split_row(sidebar, content)

        # Now split the root layout
        self.layout.split_column(header, main, footer)

    async def start(self):
        """Start the interactive CLI."""
        try:
            await self._show_welcome()
            await self._check_server_connection()
            await self._initialize_serena()
            await self._detect_and_show_project()
            await self._main_loop()
        except KeyboardInterrupt:
            await self._shutdown()
        except Exception as e:
            self.console.print(f"[red]Fatal error: {e}[/red]")
            if self.debug_mode:
                self.console.print(traceback.format_exc())
        finally:
            await self._cleanup()

    async def _show_welcome(self):
        """Show welcome screen."""
        # Count available tools
        tool_count = len(self.tool_manager.list_tools())

        welcome_text = f"""
# Plato Interactive CLI

🤖 **AI-Powered Development Assistant**  
Intelligent code analysis, generation, and refactoring with multi-provider AI routing.

**✨ Key Features:**
- 🔧 **{tool_count} Embedded Tools** - File operations, code analysis, and LSP features
- 🤖 **Multi-AI Support** - Claude, GPT-4, Gemini, and local models
- 🧠 **Smart Tool Use** - AI automatically selects and executes appropriate tools
- 💬 **Context-Aware Chat** - Maintains project context across conversations
- 🌳 **File Explorer** - Interactive project navigation
- 🔍 **Code Intelligence** - LSP-powered analysis and refactoring

**Quick Start:**
- `/help` - Show all commands and examples
- `/tools` - List {tool_count} available embedded tools  
- `/project` - Show project information
- `/debug` - Enable detailed logging

**💡 Try these examples:**
- "Show me the README file"
- "Find all functions in main.py"
- "Create a new test file"
- "Search for TODO comments"

Type your message to start chatting! The AI has full access to all tools.
        """

        panel = Panel(
            Markdown(welcome_text),
            title="[bold blue]Welcome to Plato[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )

        self.console.print(panel)
        self.console.print()

    async def _check_server_connection(self):
        """Check connection to Plato server."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Connecting to Plato server...", total=None)

            try:
                response = await self.client.get(f"{self.server_url}/health")
                response.raise_for_status()
                health_data = response.json()

                self.console.print("[green]✓ Connected to Plato server[/green]")

                # Show server status
                table = Table(
                    title="Server Status", show_header=True, header_style="bold cyan"
                )
                table.add_column("Component", style="cyan")
                table.add_column("Status", justify="center")
                table.add_column("Details")

                # Server info
                table.add_row(
                    "Server",
                    "[green]Online[/green]",
                    f"Uptime: {health_data.get('uptime', 0):.1f}s",
                )

                # AI providers
                for provider, status in health_data.get("ai_providers", {}).items():
                    status_text = "[green]✓[/green]" if status else "[red]✗[/red]"
                    table.add_row(f"AI: {provider}", status_text, "")

                # Embedded tools status
                embedded_status = health_data.get("mcp_servers", {})
                if "embedded_tools" in embedded_status:
                    status_text = (
                        "[green]✓[/green]"
                        if embedded_status["embedded_tools"]
                        else "[red]✗[/red]"
                    )
                    tool_count = embedded_status.get("tool_count", 0)
                    table.add_row("Embedded Tools", status_text, f"{tool_count} tools")

                self.console.print(table)
                self.console.print()

            except Exception as e:
                self.console.print(
                    f"[red]✗ Failed to connect to Plato server: {e}[/red]"
                )
                self.console.print(
                    "[yellow]Make sure the Plato server is running on {self.server_url}[/yellow]"
                )
                raise

    async def _initialize_serena(self):
        """Serena MCP removed - using embedded tools only."""
        self.serena_client = None

    async def _detect_and_show_project(self):
        """Detect and show project information."""
        project_summary = self.project_context.get_summary()

        # Create project info panel
        info_items = [
            f"**Name:** {project_summary['name']}",
            f"**Type:** {project_summary['type']}",
            f"**Language:** {project_summary['language']}",
            f"**Path:** {project_summary['path']}",
        ]

        if project_summary.get("git"):
            git_info = project_summary["git"]
            if "error" not in git_info:
                info_items.extend(
                    [
                        f"**Git Branch:** {git_info['branch']}",
                        f"**Status:** {'Modified' if git_info['dirty'] else 'Clean'}",
                    ]
                )

        if project_summary["config_files"]:
            info_items.append(
                f"**Config Files:** {', '.join(project_summary['config_files'])}"
            )

        project_info = Panel(
            "\n".join(info_items),
            title="[bold green]Project Detected[/bold green]",
            border_style="green",
        )

        self.console.print(project_info)
        self.console.print()

        # Activate project in Serena if available
        if self.serena_client:
            try:
                result = await self.serena_client.activate_project(
                    project_summary["path"]
                )
                if result.success:
                    self.console.print("[green]✓ Project activated in Serena[/green]")
                else:
                    self.console.print(
                        f"[yellow]⚠ Could not activate project in Serena: {result.error}[/yellow]"
                    )
            except Exception as e:
                self.console.print(
                    f"[yellow]⚠ Serena project activation failed: {e}[/yellow]"
                )

        self.console.print()

    async def _main_loop(self):
        """Main interactive loop."""
        self.console.print(
            "[dim]Ready! Type your message or use /help for commands.[/dim]"
        )
        self.console.print()

        while self.running:
            try:
                # Show context in header
                self._update_header()

                # Get user input
                user_input = Prompt.ask(
                    "[bold cyan]You[/bold cyan]", console=self.console
                ).strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    await self._handle_command(user_input)
                else:
                    await self._handle_chat_message(user_input)

                self.console.print()

            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                if self.debug_mode:
                    self.console.print(traceback.format_exc())

    def _update_header(self):
        """Update the header with current context."""
        header_text = Text()
        header_text.append("Plato Interactive CLI", style="bold blue")
        header_text.append(" | ", style="dim")
        header_text.append(self.session_manager.get_context_summary(), style="dim")

        # Rich Layout objects don't have an update method
        # Instead, we need to use a Live display or recreate the layout
        # For now, just log the update (the actual display will be handled elsewhere)
        pass  # The header update is handled in the main loop

    async def _handle_command(self, command: str):
        """Handle CLI commands."""
        parts = command[1:].split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "help":
            await self._show_help()
        elif cmd == "project":
            await self._show_project_info()
        elif cmd == "files":
            await self._toggle_file_tree()
        elif cmd == "tools":
            await self._show_tools()
        elif cmd == "provider":
            await self._set_provider(args[0] if args else None)
        elif cmd == "clear":
            await self._clear_conversation()
        elif cmd == "debug":
            self._toggle_debug()
        elif cmd == "read":
            await self._read_file(args[0] if args else None)
        elif cmd == "search":
            await self._search_project(" ".join(args) if args else None)
        elif cmd == "analyze":
            await self._analyze_file(args[0] if args else None)
        elif cmd == "tool" or cmd == "execute":
            await self._execute_tool(" ".join(args) if args else None)
        elif cmd == "write":
            await self._write_file(args[0] if args else None)
        elif cmd == "edit":
            await self._edit_file(args[0] if args else None)
        elif cmd == "mkdir":
            await self._make_directory(args[0] if args else None)
        elif cmd == "quit" or cmd == "exit":
            self.running = False
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("Type [cyan]/help[/cyan] for available commands.")

    async def _show_help(self):
        """Show help information."""
        help_text = """
## Available Commands

**💬 Chat & Interaction:**
- `/clear` - Clear conversation history
- `/provider <name>` - Set preferred AI provider (claude, gpt-4, gemini, etc.)
- `/debug` - Toggle debug mode for detailed error information

**📁 Project Navigation:**
- `/project` - Show detailed project information
- `/files` - Toggle file tree display
- `/read <path>` - Read and display a file with syntax highlighting
- `/search <pattern>` - Search for patterns in project files
- `/analyze <path>` - Analyze a file with Serena LSP (if available)

**🛠️ Tool Operations:**
- `/tools` - List all available embedded tools with descriptions
- `/tool <name> [params]` - Execute a tool directly
  Examples:
  • `/tool ReadFileTool main.py` - Read a file
  • `/tool SearchFilesTool TODO` - Search for pattern
  • `/tool ListDirectoryTool src/` - List directory contents
- `/write <path>` - Interactive file writing
- `/edit <path>` - Interactive file editing
- `/mkdir <path>` - Create a directory

**🤖 AI-Powered Features:**
The AI assistant has full access to all embedded tools and can:
• Read and analyze files during conversation
• Write and edit code based on your requests
• Search through your codebase
• Perform code analysis with LSP tools
• Execute multiple tools in sequence to complete complex tasks

**💡 Natural Language Examples:**
- "Show me the main.py file and explain what it does"
- "Find all TODO comments and create a task list"
- "Analyze the structure of the database module"
- "Create a new test file for the user service"
- "Refactor this function to use async/await"

**Tips:**
• The AI automatically selects and uses appropriate tools
• Tool results are displayed inline in the conversation
• You can see tool execution in real-time
• Use `/debug` to see detailed tool execution logs
        """

        panel = Panel(
            Markdown(help_text),
            title="[bold yellow]Help[/bold yellow]",
            border_style="yellow",
        )

        self.console.print(panel)

    async def _show_project_info(self):
        """Show detailed project information."""
        project_summary = self.project_context.get_summary()

        # Create detailed project table
        table = Table(
            title="Project Information", show_header=True, header_style="bold cyan"
        )
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value", style="white")

        table.add_row("Name", project_summary["name"])
        table.add_row("Path", project_summary["path"])
        table.add_row("Type", project_summary["type"])
        table.add_row("Language", project_summary["language"])

        if project_summary["config_files"]:
            table.add_row("Config Files", ", ".join(project_summary["config_files"]))

        if project_summary.get("git") and "error" not in project_summary["git"]:
            git_info = project_summary["git"]
            table.add_row("Git Branch", git_info["branch"])
            table.add_row("Git Status", "Modified" if git_info["dirty"] else "Clean")
            if git_info["remote"]:
                table.add_row("Git Remote", git_info["remote"])

        self.console.print(table)

        # Show file tree if enabled
        if self.show_file_tree:
            self.console.print()
            tree = self.file_explorer.build_tree()
            self.console.print(
                Panel(tree, title="[bold green]Project Structure[/bold green]")
            )

    async def _toggle_file_tree(self):
        """Toggle file tree display."""
        self.show_file_tree = not self.show_file_tree
        status = "enabled" if self.show_file_tree else "disabled"
        self.console.print(f"[green]File tree display {status}[/green]")

        if self.show_file_tree:
            tree = self.file_explorer.build_tree()
            self.console.print(
                Panel(tree, title="[bold green]Project Files[/bold green]")
            )

    async def _show_tools(self):
        """Show available tools."""
        # Get all embedded tools
        tool_names = self.tool_manager.list_tools()

        if not tool_names:
            self.console.print("[yellow]No embedded tools available[/yellow]")
        else:
            # Group tools by category
            file_tools = []
            lsp_tools = []

            for tool_name in tool_names:
                tool = self.tool_manager.get_tool(tool_name)
                if tool:
                    if (
                        "LSP" in tool_name
                        or "Symbol" in tool_name
                        or "Reference" in tool_name
                        or "Definition" in tool_name
                        or "Diagnostic" in tool_name
                        or "Analysis" in tool_name
                        or "Hover" in tool_name
                        or "Completion" in tool_name
                    ):
                        lsp_tools.append((tool_name, tool))
                    else:
                        file_tools.append((tool_name, tool))

            # Show file operation tools
            if file_tools:
                self.console.print("[bold cyan]📁 File Operation Tools:[/bold cyan]")
                file_table = Table(show_header=True, header_style="bold cyan", box=None)
                file_table.add_column("Tool", style="green", width=25)
                file_table.add_column("Description", style="white")

                for tool_name, tool in sorted(file_tools):
                    description = tool.description
                    if len(description) > 70:
                        description = description[:67] + "..."
                    file_table.add_row(f"• {tool_name}", description)

                self.console.print(file_table)
                self.console.print()

            # Show LSP/code analysis tools
            if lsp_tools:
                self.console.print(
                    "[bold cyan]🔍 Code Analysis Tools (LSP):[/bold cyan]"
                )
                lsp_table = Table(show_header=True, header_style="bold cyan", box=None)
                lsp_table.add_column("Tool", style="green", width=25)
                lsp_table.add_column("Description", style="white")

                for tool_name, tool in sorted(lsp_tools):
                    description = tool.description
                    if len(description) > 70:
                        description = description[:67] + "..."
                    lsp_table.add_row(f"• {tool_name}", description)

                self.console.print(lsp_table)
                self.console.print()

            # Show usage examples
            self.console.print("[bold yellow]Usage Examples:[/bold yellow]")
            examples = [
                "• Direct execution: [cyan]/tool ReadFileTool file.py[/cyan]",
                "• Natural language: [cyan]Show me the main.py file[/cyan]",
                "• AI with tools: [cyan]Analyze the structure of app.py and find all TODO comments[/cyan]",
                '• JSON format: [cyan]/tool {"tool": "SearchFilesTool", "parameters": {"pattern": "TODO"}}[/cyan]',
            ]
            for example in examples:
                self.console.print(f"  {example}")
            self.console.print()

        # Show server-side embedded tools if available
        try:
            response = await self.client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            tools_data = response.json()

            if tools_data.get("tools"):
                self.console.print("[bold cyan]Server Tools:[/bold cyan]")
                server_table = Table(show_header=True, header_style="bold cyan")
                server_table.add_column("Name", style="cyan", width=25)
                server_table.add_column("Type", style="green", width=15)
                server_table.add_column("Description", style="white")

                for tool in tools_data["tools"]:
                    description = tool["description"]
                    if len(description) > 60:
                        description = description[:57] + "..."

                    server_table.add_row(
                        tool["name"], tool.get("type", "embedded"), description
                    )

                self.console.print(server_table)

        except Exception as e:
            self.console.print(f"[yellow]Server tools unavailable: {e}[/yellow]")

    async def _set_provider(self, provider_name: Optional[str]):
        """Set preferred AI provider."""
        if not provider_name:
            self.console.print(
                "Available providers: claude, gpt-4, gpt-3.5-turbo, gemini, qwen-local, openrouter"
            )
            return

        # Validate provider
        valid_providers = [p.value for p in AIProvider]
        if provider_name not in valid_providers:
            self.console.print(f"[red]Invalid provider: {provider_name}[/red]")
            self.console.print(f"Available: {', '.join(valid_providers)}")
            return

        self.session_manager.current_provider = provider_name
        self.console.print(f"[green]Set preferred provider to: {provider_name}[/green]")

    async def _clear_conversation(self):
        """Clear conversation history."""
        self.session_manager.messages.clear()
        self.session_manager.session_id = None
        self.session_manager.tokens_used = 0
        self.console.print("[green]Conversation cleared[/green]")

    def _toggle_debug(self):
        """Toggle debug mode."""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        self.console.print(f"[green]Debug mode {status}[/green]")

    async def _read_file(self, file_path: Optional[str]):
        """Read and display a file."""
        if not file_path:
            file_path = Prompt.ask("Enter file path")

        try:
            # Try using Serena first for better context
            if self.serena_client:
                result = await self.serena_client.read_file(file_path)
                if result.success:
                    content = result.data

                    # Detect language for syntax highlighting
                    language = "text"
                    if HAS_PYGMENTS:
                        try:
                            lexer = get_lexer_for_filename(file_path)
                            language = lexer.aliases[0] if lexer.aliases else "text"
                        except ClassNotFound:
                            pass

                    syntax = Syntax(
                        content, language, theme="monokai", line_numbers=True
                    )
                    panel = Panel(
                        syntax,
                        title=f"[bold green]{file_path}[/bold green]",
                        border_style="green",
                    )

                    self.console.print(panel)
                    return

            # Fallback to local file reading
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = self.project_context.path / file_path

            if not full_path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                return

            content = full_path.read_text(encoding="utf-8")

            # Detect language for syntax highlighting
            language = "text"
            if HAS_PYGMENTS:
                try:
                    lexer = get_lexer_for_filename(str(full_path))
                    language = lexer.aliases[0] if lexer.aliases else "text"
                except ClassNotFound:
                    pass

            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            panel = Panel(
                syntax,
                title=f"[bold green]{file_path}[/bold green]",
                border_style="green",
            )

            self.console.print(panel)

        except Exception as e:
            self.console.print(f"[red]Failed to read file: {e}[/red]")

    async def _search_project(self, pattern: Optional[str]):
        """Search for patterns in project files."""
        if not pattern:
            pattern = Prompt.ask("Enter search pattern")

        try:
            if self.serena_client:
                result = await self.serena_client.search_for_pattern(pattern)
                if result.success:
                    self.console.print(
                        f"[green]Search results for '{pattern}':[/green]"
                    )

                    # Format and display results
                    if isinstance(result.data, str):
                        self.console.print(Panel(result.data, title="Search Results"))
                    else:
                        self.console.print(result.data)
                    return

            # Fallback to simple grep-like search
            self.console.print(
                f"[yellow]Searching for '{pattern}' (basic search)...[/yellow]"
            )

            matches = []
            for file_path in self.project_context.path.rglob("*"):
                if file_path.is_file() and not any(
                    part.startswith(".") for part in file_path.parts
                ):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        lines = content.split("\n")
                        for line_num, line in enumerate(lines, 1):
                            if pattern.lower() in line.lower():
                                relative_path = file_path.relative_to(
                                    self.project_context.path
                                )
                                matches.append(
                                    f"{relative_path}:{line_num}: {line.strip()}"
                                )
                                if len(matches) > 50:  # Limit results
                                    break
                    except Exception:
                        continue

                if len(matches) > 50:
                    break

            if matches:
                results_text = "\n".join(matches[:20])  # Show first 20 matches
                if len(matches) > 20:
                    results_text += f"\n... and {len(matches) - 20} more matches"

                panel = Panel(
                    results_text,
                    title=f"[bold green]Search Results for '{pattern}'[/bold green]",
                )
                self.console.print(panel)
            else:
                self.console.print(f"[yellow]No matches found for '{pattern}'[/yellow]")

        except Exception as e:
            self.console.print(f"[red]Search failed: {e}[/red]")

    async def _analyze_file(self, file_path: Optional[str]):
        """Analyze a file with Serena LSP."""
        if not file_path:
            file_path = Prompt.ask("Enter file path to analyze")

        if not self.serena_client:
            self.console.print(
                "[red]Code analysis not available (using embedded tools only)[/red]"
            )
            return

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task(f"Analyzing {file_path}...", total=None)

                # Get symbols overview
                result = await self.serena_client.get_symbols_overview(file_path)

                if result.success:
                    self.console.print(
                        f"[green]Analysis complete for {file_path}[/green]"
                    )

                    # Display symbols information
                    if isinstance(result.data, str):
                        panel = Panel(
                            result.data,
                            title=f"[bold blue]Symbols in {file_path}[/bold blue]",
                        )
                        self.console.print(panel)
                    else:
                        self.console.print(result.data)
                else:
                    self.console.print(f"[red]Analysis failed: {result.error}[/red]")

        except Exception as e:
            self.console.print(f"[red]Analysis error: {e}[/red]")

    async def _execute_tool(self, tool_spec: Optional[str]):
        """Execute an embedded tool."""
        if not tool_spec:
            # Show available tools
            await self._show_tools()
            return

        # Parse tool specification
        parts = tool_spec.split(maxsplit=1)
        if not parts:
            await self._show_tools()
            return

        tool_name = parts[0]
        params_text = parts[1] if len(parts) > 1 else ""

        # Check if tool exists
        tool = self.tool_manager.get_tool(tool_name)
        if not tool:
            # Try to parse as natural language or JSON
            try:
                result = await self.tool_manager.execute_from_text(tool_spec)
                if result:
                    output = self.tool_manager.format_tool_result(result)
                    self.console.print(
                        Panel(
                            output,
                            title="[bold green]Tool Result[/bold green]",
                            border_style="green",
                        )
                    )
                else:
                    self.console.print(
                        f"[yellow]Tool '{tool_name}' not found. Available tools:[/yellow]"
                    )
                    for available_tool in sorted(self.tool_manager.list_tools()):
                        self.console.print(f"  • {available_tool}")
            except Exception as e:
                self.console.print(f"[red]Tool execution failed: {e}[/red]")
                if self.debug_mode:
                    self.console.print(traceback.format_exc())
            return

        # Parse parameters
        params = {}
        if params_text:
            # Try JSON first
            if params_text.startswith("{"):
                try:
                    params = json.loads(params_text)
                except json.JSONDecodeError:
                    pass

            # If not JSON, try to parse as key=value pairs or positional
            if not params:
                # Simple heuristic for common tools
                if tool_name == "ReadFileTool":
                    params = {"file_path": params_text}
                elif tool_name == "WriteFileTool":
                    # For write, we need both path and content
                    if " " in params_text:
                        path, content = params_text.split(maxsplit=1)
                        params = {"file_path": path, "content": content}
                    else:
                        self.console.print(
                            "[yellow]WriteFileTool requires: /tool WriteFileTool <path> <content>[/yellow]"
                        )
                        return
                elif tool_name == "SearchFilesTool":
                    params = {"pattern": params_text}
                elif tool_name == "ListDirectoryTool":
                    params = {"directory_path": params_text or "."}
                elif tool_name == "CreateDirectoryTool":
                    params = {"directory_path": params_text}
                elif tool_name == "EditFileTool":
                    self.console.print(
                        "[yellow]EditFileTool requires JSON format with file_path, old_content, and new_content[/yellow]"
                    )
                    return
                else:
                    # For other tools, try to be smart about parameters
                    params = {"file_path": params_text}  # Default assumption

        # Execute the tool
        try:
            self.console.print(f"[cyan]Executing {tool_name}...[/cyan]")
            result = await self.tool_manager.execute_tool(tool_name, **params)
            output = self.tool_manager.format_tool_result(result)

            # Format output nicely based on tool type
            if result.success:
                if tool_name == "ReadFileTool" and result.data:
                    # For file reading, show with syntax highlighting
                    language = "text"
                    if HAS_PYGMENTS and "file_path" in params:
                        try:
                            from pygments.lexers import get_lexer_for_filename

                            lexer = get_lexer_for_filename(params["file_path"])
                            language = lexer.aliases[0] if lexer.aliases else "text"
                        except:
                            pass

                    syntax = Syntax(
                        result.data, language, theme="monokai", line_numbers=True
                    )
                    self.console.print(
                        Panel(
                            syntax,
                            title=f"[bold green]{params.get('file_path', 'File Content')}[/bold green]",
                            border_style="green",
                        )
                    )
                else:
                    self.console.print(
                        Panel(
                            output,
                            title=f"[bold green]{tool_name} Result[/bold green]",
                            border_style="green",
                        )
                    )
            else:
                self.console.print(
                    Panel(
                        output,
                        title=f"[bold red]{tool_name} Error[/bold red]",
                        border_style="red",
                    )
                )

        except Exception as e:
            self.console.print(f"[red]Tool execution failed: {e}[/red]")
            if self.debug_mode:
                self.console.print(traceback.format_exc())

    async def _write_file(self, file_path: Optional[str]):
        """Write content to a file."""
        if not file_path:
            file_path = Prompt.ask("Enter file path")

        self.console.print(
            "Enter content (end with Ctrl+D on Unix or Ctrl+Z on Windows):"
        )
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        content = "\n".join(lines)

        try:
            result = await self.tool_manager.execute_tool(
                "WriteFileTool", file_path=file_path, content=content
            )
            output = self.tool_manager.format_tool_result(result)
            self.console.print(
                Panel(output, title="[bold green]Write Result[/bold green]")
            )
        except Exception as e:
            self.console.print(f"[red]Write failed: {e}[/red]")

    async def _edit_file(self, file_path: Optional[str]):
        """Edit a file interactively."""
        if not file_path:
            file_path = Prompt.ask("Enter file path to edit")

        # First read the file
        try:
            result = await self.tool_manager.execute_tool(
                "ReadFileTool", file_path=file_path
            )
            if not result.success:
                self.console.print(f"[red]Cannot read file: {result.error}[/red]")
                return

            self.console.print(
                Panel(result.data, title=f"[bold]Current content of {file_path}[/bold]")
            )

            old_content = Prompt.ask("Enter text to replace (exact match)")
            new_content = Prompt.ask("Enter replacement text")

            result = await self.tool_manager.execute_tool(
                "EditFileTool",
                file_path=file_path,
                old_content=old_content,
                new_content=new_content,
            )
            output = self.tool_manager.format_tool_result(result)
            self.console.print(
                Panel(output, title="[bold green]Edit Result[/bold green]")
            )
        except Exception as e:
            self.console.print(f"[red]Edit failed: {e}[/red]")

    async def _make_directory(self, dir_path: Optional[str]):
        """Create a directory."""
        if not dir_path:
            dir_path = Prompt.ask("Enter directory path")

        try:
            result = await self.tool_manager.execute_tool(
                "CreateDirectoryTool", directory_path=dir_path
            )
            output = self.tool_manager.format_tool_result(result)
            self.console.print(
                Panel(output, title="[bold green]Directory Created[/bold green]")
            )
        except Exception as e:
            self.console.print(f"[red]Failed to create directory: {e}[/red]")

    async def _handle_chat_message(self, message: str):
        """Handle regular chat messages."""
        # Add user message to session
        self.session_manager.add_message("user", message)

        # Build context for the request
        context = await self._build_request_context()

        # Determine task type based on message content
        task_type = self._infer_task_type(message)

        # Send to Plato server
        await self._send_chat_request(message, task_type, context)

    async def _build_request_context(self) -> Dict[str, Any]:
        """Build context for AI request."""
        context = {
            "project": self.project_context.get_summary(),
            "session": {
                "messages": self.session_manager.messages[-10:],  # Last 10 messages
                "session_id": self.session_manager.session_id,
            },
        }

        # Add file context if relevant
        if self.auto_context and self.file_explorer.current_file:
            try:
                if self.serena_client:
                    file_context = await self.serena_client.build_file_context(
                        self.file_explorer.current_file
                    )
                    context["current_file"] = file_context
            except Exception as e:
                if self.debug_mode:
                    self.console.print(
                        f"[yellow]Warning: Could not build file context: {e}[/yellow]"
                    )

        return context

    def _infer_task_type(self, message: str) -> TaskType:
        """Infer task type from message content."""
        message_lower = message.lower()

        if any(
            word in message_lower
            for word in ["analyze", "analysis", "structure", "symbols"]
        ):
            return TaskType.CODE_ANALYSIS
        elif any(
            word in message_lower
            for word in ["generate", "create", "write", "implement"]
        ):
            return TaskType.CODE_GENERATION
        elif any(
            word in message_lower
            for word in ["refactor", "improve", "optimize", "clean"]
        ):
            return TaskType.REFACTORING
        elif any(
            word in message_lower for word in ["document", "docs", "comment", "explain"]
        ):
            return TaskType.DOCUMENTATION
        elif any(word in message_lower for word in ["tool", "run", "execute", "call"]):
            return TaskType.TOOL_USE
        else:
            return TaskType.CHAT

    async def _send_chat_request(
        self, message: str, task_type: TaskType, context: Dict[str, Any]
    ):
        """Send chat request to Plato server."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Thinking...", total=None)

            try:
                # Get tool schemas in OpenAI format for AI
                tool_schemas = self.tool_manager.get_openai_tool_schemas()

                # Add embedded tools information to context
                context["embedded_tools"] = tool_schemas
                context["tool_descriptions"] = self.tool_manager.format_tools_for_ai()

                # Add last tool results if available
                if (
                    hasattr(self.session_manager, "context")
                    and "last_tool_results" in self.session_manager.context
                ):
                    context["last_tool_results"] = self.session_manager.context[
                        "last_tool_results"
                    ]

                # Create system message that includes tool information
                tool_system_message = f"""You have access to the following embedded tools:

{self.tool_manager.format_tools_for_ai()}

To use a tool, respond with a tool call in one of these formats:
1. JSON: TOOL_CALL: {{"tool": "ToolName", "parameters": {{...}}}}
2. Markdown: ```tool {{"tool": "ToolName", "parameters": {{...}}}} ```

Always use tools when appropriate to help answer the user's questions or complete tasks.
"""

                payload = {
                    "message": message,
                    "task_type": task_type.value,
                    "stream": False,
                    "context": context,
                    "tools": tool_schemas,  # Include tool schemas
                    "system_message": tool_system_message,  # Add system message about tools
                }

                if self.session_manager.session_id:
                    payload["session_id"] = self.session_manager.session_id

                if self.session_manager.current_provider:
                    payload["preferred_provider"] = (
                        self.session_manager.current_provider
                    )

                response = await self.client.post(
                    f"{self.server_url}/chat", json=payload
                )
                response.raise_for_status()
                result = response.json()

                # Update session
                self.session_manager.session_id = result["session_id"]
                self.session_manager.current_provider = result["provider"]
                self.session_manager.tokens_used += result["tokens_used"]
                self.session_manager.add_message(
                    "assistant",
                    result["message"],
                    {"provider": result["provider"], "tokens": result["tokens_used"]},
                )

                # Display response first
                self._display_ai_response(result)

                # Then check if AI requested tool use
                await self._handle_ai_tool_requests(result)

            except httpx.HTTPStatusError as e:
                self.console.print(
                    f"[red]Chat request failed with HTTP {e.response.status_code}: {e.response.text}[/red]"
                )
                if self.debug_mode:
                    self.console.print(
                        f"[yellow]Request payload keys: {list(payload.keys())}[/yellow]"
                    )
                    self.console.print(
                        f"[yellow]Tools count: {len(tool_schemas) if tool_schemas else 0}[/yellow]"
                    )
                    self.console.print(traceback.format_exc())
            except Exception as e:
                self.console.print(f"[red]Chat request failed: {e}[/red]")
                if self.debug_mode:
                    self.console.print(
                        f"[yellow]Request payload keys: {list(payload.keys())}[/yellow]"
                    )
                    self.console.print(
                        f"[yellow]Tools count: {len(tool_schemas) if tool_schemas else 0}[/yellow]"
                    )
                    self.console.print(traceback.format_exc())

    async def _handle_ai_tool_requests(self, response: Dict[str, Any]):
        """Handle tool requests from AI response."""
        # Check for tool calls in metadata
        metadata = response.get("metadata", {})
        tool_calls = metadata.get("tool_calls", [])
        tool_results = []
        message = response.get("message", "")  # Get message early for broader scope

        if self.debug_mode:
            self.console.print(f"[yellow]DEBUG: Checking for tool calls in response[/yellow]")
            self.console.print(f"[yellow]DEBUG: Metadata tool_calls: {tool_calls}[/yellow]")

        if not tool_calls:
            # Try to extract tool calls from the message itself
            if self.debug_mode:
                self.console.print(f"[yellow]DEBUG: Parsing message for tool calls: {message[:200]}...[/yellow]")

            # Look for various tool call patterns
            import re

            # Pattern 1: TOOL_CALL: {...}
            # Pattern 2: ```tool {...} ```
            # Pattern 3: <tool>...</tool>
            # Pattern 4: Tool: name, Parameters: {...}
            # Pattern 5: <tool_call><function=...><parameter=...>...</tool_call>
            patterns = [
                r"TOOL_CALL:\s*(\{(?:[^{}]|{[^{}]*})*\})",
                r"```tool\s*(\{.*?\})\s*```",
                r"<tool>([^<]+)</tool>",
                r"Tool:\s*(\w+),?\s*Parameters:\s*(\{(?:[^{}]|{[^{}]*})*\})",
                r"<tool_call>(.*?)</tool_call>",
            ]

            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, message, re.DOTALL)
                for match in matches:
                    try:
                        if isinstance(match, tuple):
                            # Pattern 4: separate tool name and params
                            tool_name = match[0]
                            params = json.loads(match[1])
                            tool_calls.append({"tool": tool_name, "parameters": params})
                        elif i == 4:  # Pattern 5: <tool_call>...</tool_call>
                            # Parse XML-like format
                            tool_content = match
                            
                            if self.debug_mode:
                                self.console.print(f"[yellow]DEBUG: Parsing XML tool call: {tool_content[:100]}...[/yellow]")
                            
                            # Extract function name
                            func_match = re.search(r"<function=([^>]+)>", tool_content)
                            if not func_match:
                                if self.debug_mode:
                                    self.console.print(f"[yellow]DEBUG: No function found in tool call[/yellow]")
                                continue
                            tool_name = func_match.group(1)
                            
                            if self.debug_mode:
                                self.console.print(f"[yellow]DEBUG: Extracted tool name: {tool_name}[/yellow]")
                            
                            # Extract parameters
                            param_pattern = r"<parameter=([^>]+)>([^<]*)</parameter>"
                            param_matches = re.findall(param_pattern, tool_content)
                            
                            # Fallback for parameters without closing tags
                            if not param_matches:
                                param_pattern = r"<parameter=([^>]+)>([^<]*)"
                                param_matches = re.findall(param_pattern, tool_content)
                            
                            params = {}
                            for param_name, param_value in param_matches:
                                params[param_name] = param_value.strip()
                            
                            if self.debug_mode:
                                self.console.print(f"[yellow]DEBUG: Extracted parameters: {params}[/yellow]")
                            
                            tool_calls.append({"tool": tool_name, "parameters": params})
                        else:
                            # JSON patterns
                            tool_request = json.loads(match)
                            tool_calls.append(tool_request)
                    except (json.JSONDecodeError, IndexError) as e:
                        if self.debug_mode:
                            self.console.print(f"[yellow]DEBUG: Failed to parse tool call: {e}[/yellow]")

        # Always show tool calls found (not just in debug mode)
        if tool_calls:
            self.console.print(f"[cyan]📋 Found {len(tool_calls)} tool call(s) to execute[/cyan]")
            if self.debug_mode:
                for i, call in enumerate(tool_calls):
                    self.console.print(f"[yellow]DEBUG: Tool call {i}: {call}[/yellow]")
        elif self.debug_mode:
            # Show when no tool calls are found (in debug mode)
            self.console.print(f"[yellow]DEBUG: No tool calls found in response[/yellow]")
            if message and "<tool_call>" in message:
                self.console.print(f"[yellow]DEBUG: Message contains '<tool_call>' but parsing failed[/yellow]")

        # Execute tool calls
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool") or tool_call.get("name")
            parameters = tool_call.get("parameters", {})

            if tool_name:
                self.console.print(f"[cyan]🔧 Executing tool: {tool_name}[/cyan]")
                try:
                    result = await self.tool_manager.execute_tool(
                        tool_name, **parameters
                    )

                    # Store result for potential follow-up
                    tool_results.append(
                        {"tool": tool_name, "parameters": parameters, "result": result}
                    )

                    # Display result nicely
                    if result.success:
                        # Special handling for different tool types
                        if tool_name == "ReadFileTool" and result.data:
                            # Show file content with syntax highlighting
                            file_path = parameters.get("file_path", "unknown")
                            language = "text"
                            if HAS_PYGMENTS:
                                try:
                                    from pygments.lexers import get_lexer_for_filename

                                    lexer = get_lexer_for_filename(file_path)
                                    language = (
                                        lexer.aliases[0] if lexer.aliases else "text"
                                    )
                                except:
                                    pass

                            syntax = Syntax(
                                result.data[:1000],
                                language,
                                theme="monokai",
                                line_numbers=True,
                            )
                            if len(result.data) > 1000:
                                syntax = Text(result.data[:1000] + "\n... (truncated)")

                            self.console.print(
                                Panel(
                                    syntax,
                                    title=f"[bold blue]📄 {file_path}[/bold blue]",
                                    border_style="blue",
                                )
                            )
                        elif tool_name == "WriteFileTool" and result.data:
                            # Show write file result
                            self.console.print(
                                Panel(
                                    f"[green]✅ {result.data}[/green]",
                                    title=f"[bold blue]📝 {tool_name}[/bold blue]",
                                    border_style="blue",
                                )
                            )
                        else:
                            # Generic tool result display
                            output = self.tool_manager.format_tool_result(result) if hasattr(self.tool_manager, 'format_tool_result') else str(result.data)
                            self.console.print(
                                Panel(
                                    output,
                                    title=f"[bold blue]🔧 {tool_name}[/bold blue]",
                                    border_style="blue",
                                )
                            )
                    else:
                        self.console.print(
                            Panel(
                                f"[red]❌ {result.error}[/red]",
                                title=f"[bold red]Tool Error: {tool_name}[/bold red]",
                                border_style="red",
                            )
                        )

                except Exception as e:
                    self.console.print(f"[red]Tool execution failed: {e}[/red]")
                    if self.debug_mode:
                        self.console.print(traceback.format_exc())

        # If we executed tools, offer to send results back to AI
        if tool_results and len(self.session_manager.messages) > 0:
            # Add tool results to context for next message
            self.session_manager.context["last_tool_results"] = tool_results

    def _display_ai_response(self, response: Dict[str, Any]):
        """Display AI response with rich formatting."""
        provider = response.get("provider", "AI")
        message = response.get("message", "")
        tokens = response.get("tokens_used", 0)

        # Create header with provider info
        header = Text()
        header.append(f"🤖 {provider.upper()}", style="bold green")
        header.append(f" ({tokens} tokens)", style="dim")

        # Parse and render markdown content
        try:
            # Check if response contains code blocks or structured content
            if "```" in message or message.startswith("#"):
                content = Markdown(message)
            else:
                content = Text(message)

            panel = Panel(content, title=header, border_style="green", padding=(1, 2))

            self.console.print(panel)

        except Exception:
            # Fallback to simple text display
            panel = Panel(message, title=header, border_style="green", padding=(1, 2))
            self.console.print(panel)

    async def _shutdown(self):
        """Handle shutdown procedures."""
        self.console.print("\n[yellow]Shutting down Plato...[/yellow]")
        self.running = False

    async def _cleanup(self):
        """Cleanup resources."""
        try:
            if self.serena_client:
                await self.serena_client.disconnect()
            await self.client.aclose()
        except Exception as e:
            if self.debug_mode:
                self.console.print(f"[yellow]Cleanup warning: {e}[/yellow]")


async def main(server_url: str = "http://localhost:8080"):
    """Main entry point for interactive CLI."""
    cli = PlatoInteractiveCLI(server_url)
    await cli.start()


if __name__ == "__main__":
    import sys

    # Get server URL from command line args
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    # Run the interactive CLI
    asyncio.run(main(server_url))
