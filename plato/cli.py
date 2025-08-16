"""CLI interface for Plato."""

import asyncio
import json

import httpx
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from plato.core.ai_router import AIProvider, TaskType

# Optional Serena integration
try:
    from plato.integrations.serena_mcp import SerenaLanguage
except ImportError:
    # Create dummy enum if Serena not available
    from enum import Enum

    class SerenaLanguage(str, Enum):
        PYTHON = "python"
        TYPESCRIPT = "typescript"
        JAVASCRIPT = "javascript"


app = typer.Typer(name="plato", help="Plato AI orchestration system CLI")
console = Console()

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:8080"


class PlatoClient:
    """Client for interacting with Plato server."""

    def __init__(self, base_url: str = DEFAULT_SERVER_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def health_check(self) -> dict:
        """Check server health."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def chat(
        self,
        message: str,
        session_id: str | None = None,
        task_type: TaskType = TaskType.CHAT,
        provider: AIProvider | None = None,
    ) -> dict:
        """Send chat message."""
        payload = {"message": message, "task_type": task_type.value, "stream": False}

        if session_id:
            payload["session_id"] = session_id
        if provider:
            payload["preferred_provider"] = provider.value

        response = await self.client.post(f"{self.base_url}/chat", json=payload)
        response.raise_for_status()
        return response.json()

    async def list_tools(self) -> dict:
        """List available tools."""
        response = await self.client.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a tool."""
        payload = {"tool_name": tool_name, "arguments": arguments}

        response = await self.client.post(f"{self.base_url}/tools/call", json=payload)
        response.raise_for_status()
        return response.json()

    async def analyze_code(
        self,
        project_path: str,
        operation: str,
        language: SerenaLanguage | None = None,
        **kwargs,
    ) -> dict:
        """Analyze code with Serena."""
        payload = {
            "project_path": project_path,
            "operation": operation,
            "parameters": kwargs,
        }

        if language:
            payload["language"] = language.value

        response = await self.client.post(
            f"{self.base_url}/serena/analyze", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client."""
        await self.client.aclose()


@app.command()
def health(server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL")):
    """Check Plato server health."""

    async def _health():
        client = PlatoClient(server_url)
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Checking server health...", total=None)
                health_data = await client.health_check()
                progress.update(task, completed=True)

            # Display health information
            table = Table(title="Plato Server Health")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details")

            # Server status
            table.add_row(
                "Server", "✓ Healthy", f"Uptime: {health_data['uptime']:.1f}s"
            )

            # AI providers
            for provider, status in health_data["ai_providers"].items():
                status_icon = "✓" if status else "✗"
                status_color = "green" if status else "red"
                table.add_row(
                    f"AI: {provider}", f"[{status_color}]{status_icon}[/]", ""
                )

            # MCP servers
            for server, status in health_data["mcp_servers"].items():
                status_icon = "✓" if status else "✗"
                status_color = "green" if status else "red"
                table.add_row(f"MCP: {server}", f"[{status_color}]{status_icon}[/]", "")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error checking health: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(_health())


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send"),
    session_id: str | None = typer.Option(None, help="Session ID"),
    task_type: TaskType = typer.Option(TaskType.CHAT, help="Task type"),
    provider: AIProvider | None = typer.Option(None, help="Preferred AI provider"),
    server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL"),
):
    """Send a chat message to Plato."""

    async def _chat():
        client = PlatoClient(server_url)
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Sending message...", total=None)
                response = await client.chat(message, session_id, task_type, provider)
                progress.update(task, completed=True)

            # Display response
            panel = Panel(
                response["message"],
                title=f"Response from {response['provider']}",
                subtitle=f"Session: {response['session_id']} | Tokens: {response['tokens_used']}",
            )
            console.print(panel)

        except Exception as e:
            console.print(f"[red]Error sending message: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(_chat())


@app.command()
def tools(server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL")):
    """List available tools."""

    async def _tools():
        client = PlatoClient(server_url)
        try:
            tools_data = await client.list_tools()

            if not tools_data["tools"]:
                console.print("[yellow]No tools available[/yellow]")
                return

            table = Table(title="Available Tools")
            table.add_column("Name", style="cyan")
            table.add_column("Server", style="green")
            table.add_column("Description")

            for tool in tools_data["tools"]:
                table.add_row(
                    tool["name"],
                    tool["server"],
                    (
                        tool["description"][:80] + "..."
                        if len(tool["description"]) > 80
                        else tool["description"]
                    ),
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error listing tools: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(_tools())


@app.command()
def call_tool(
    tool_name: str = typer.Argument(..., help="Tool name"),
    arguments: str = typer.Option("{}", help="Tool arguments as JSON"),
    server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL"),
):
    """Call a tool."""

    async def _call_tool():
        client = PlatoClient(server_url)
        try:
            # Parse arguments
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON in arguments[/red]")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Calling tool {tool_name}...", total=None)
                response = await client.call_tool(tool_name, args)
                progress.update(task, completed=True)

            # Display response
            if response["success"]:
                console.print("[green]✓ Tool call successful[/green]")
                console.print(
                    Panel(json.dumps(response["result"], indent=2), title="Result")
                )
            else:
                console.print(f"[red]✗ Tool call failed: {response['error']}[/red]")

        except Exception as e:
            console.print(f"[red]Error calling tool: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(_call_tool())


@app.command()
def analyze(
    project_path: str = typer.Argument(..., help="Project path to analyze"),
    operation: str = typer.Option("build_context", help="Analysis operation"),
    language: SerenaLanguage | None = typer.Option(None, help="Programming language"),
    file_path: str | None = typer.Option(None, help="Specific file path"),
    query: str | None = typer.Option(None, help="Search query"),
    server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL"),
):
    """Analyze code with Serena LSP."""

    async def _analyze():
        client = PlatoClient(server_url)
        try:
            # Build parameters
            params = {}
            if file_path:
                params["file_path"] = file_path
            if query:
                params["query"] = query

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Analyzing {project_path}...", total=None)
                response = await client.analyze_code(
                    project_path, operation, language, **params
                )
                progress.update(task, completed=True)

            # Display response
            if response["success"]:
                console.print("[green]✓ Analysis successful[/green]")
                console.print(
                    Panel(
                        json.dumps(response["data"], indent=2),
                        title=f"Analysis: {operation}",
                    )
                )
            else:
                console.print("[red]✗ Analysis failed[/red]")

        except Exception as e:
            console.print(f"[red]Error analyzing code: {e}[/red]")
        finally:
            await client.close()

    asyncio.run(_analyze())


@app.command()
def interactive(
    server_url: str = typer.Option(DEFAULT_SERVER_URL, help="Plato server URL")
):
    """Start interactive chat session with rich Claude Code-like interface."""
    from plato.interactive_cli import main as interactive_main

    asyncio.run(interactive_main(server_url))


def main():
    """Main CLI entry point."""
    import sys

    # If no arguments provided, default to interactive mode
    if len(sys.argv) == 1:
        from plato.interactive_cli import main as interactive_main
        import asyncio

        print("🚀 Starting Plato Interactive CLI...")
        print("   Use /help for commands or Ctrl+C to exit")
        print()
        try:
            asyncio.run(interactive_main(DEFAULT_SERVER_URL))
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Otherwise, use the normal CLI
    app()


if __name__ == "__main__":
    main()
