"""Fixed Serena MCP integration using proper MCP protocol over SSE."""

import asyncio
import logging
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Add Serena's MCP libraries to path
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

try:
    import mcp.types as types
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
except ImportError as e:
    raise ImportError(
        f"MCP libraries not available: {e}\n"
        "Please install MCP dependencies or run from Serena environment"
    )

logger = logging.getLogger(__name__)


class SerenaLanguage(str, Enum):
    """Supported languages in Serena."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    PHP = "php"
    CSHARP = "csharp"
    RUBY = "ruby"
    SWIFT = "swift"
    ELIXIR = "elixir"
    CLOJURE = "clojure"
    BASH = "bash"
    C = "c"
    CPP = "cpp"
    TERRAFORM = "terraform"


@dataclass
class SerenaResponse:
    """Serena response wrapper."""

    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_mcp_result(cls, result: types.CallToolResult) -> "SerenaResponse":
        """Create response from MCP call result."""
        if result.is_error:
            return cls(success=False, error=str(result.error))

        # Extract text content from MCP response
        content_data = None
        if result.content:
            if len(result.content) == 1:
                content = result.content[0]
                if hasattr(content, "text"):
                    content_data = content.text
                else:
                    content_data = content
            else:
                content_data = [getattr(c, "text", c) for c in result.content]

        return cls(success=True, data=content_data, metadata={"raw_result": result})


class SerenaMCPClient:
    """Proper MCP client for Serena using SSE transport."""

    def __init__(self, host: str = "localhost", port: int = 8765, timeout: int = 30):
        """Initialize Serena MCP client."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.sse_url = f"{self.base_url}/sse"

        # MCP session components
        self.session: ClientSession | None = None
        self.transport_context = None
        self.read_stream = None
        self.write_stream = None

        # Available tools cache
        self._tools: list[types.Tool] = []
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Serena MCP server using proper MCP protocol."""
        try:
            logger.info(f"Connecting to Serena MCP via SSE: {self.sse_url}")

            # Create SSE client connection to Serena
            self.transport_context = sse_client(
                self.sse_url, timeout=self.timeout, sse_read_timeout=60
            )
            self.read_stream, self.write_stream = (
                await self.transport_context.__aenter__()
            )

            # Create MCP client session
            self.session = ClientSession(
                read_stream=self.read_stream,
                write_stream=self.write_stream,
            )

            # Initialize the session
            init_result = await self.session.initialize()
            logger.info(f"MCP session initialized successfully")
            logger.info(
                f"Server: {init_result.server_info.name} v{init_result.server_info.version}"
            )

            # Cache available tools
            await self._refresh_tools()

            self._connected = True
            return True

        except Exception as e:
            logger.error(f"Failed to connect via MCP: {e}")
            await self._cleanup_connection()
            return False

    async def disconnect(self):
        """Disconnect from Serena MCP server."""
        await self._cleanup_connection()

    async def _cleanup_connection(self):
        """Clean up connection resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None

            if self.transport_context:
                await self.transport_context.__aexit__(None, None, None)
                self.transport_context = None

            self.read_stream = None
            self.write_stream = None
            self._connected = False

            logger.info("Disconnected from Serena MCP")

        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    async def _refresh_tools(self):
        """Refresh the list of available tools."""
        if not self.session:
            return

        try:
            result = await self.session.list_tools()
            self._tools = result.tools
            logger.info(f"Found {len(self._tools)} tools available")
        except Exception as e:
            logger.error(f"Failed to refresh tools: {e}")

    async def _call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> SerenaResponse:
        """Call a tool via MCP protocol."""
        if not self._connected or not self.session:
            connected = await self.connect()
            if not connected:
                return SerenaResponse(
                    success=False, error="Not connected to MCP server"
                )

        try:
            logger.debug(f"Calling tool: {tool_name} with args: {arguments}")

            # Use MCP protocol to call tool
            result = await self.session.call_tool(tool_name, arguments)

            return SerenaResponse.from_mcp_result(result)

        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return SerenaResponse(success=False, error=str(e))

    # Project Management
    async def activate_project(self, project_path: str) -> SerenaResponse:
        """Activate a project in Serena."""
        return await self._call_tool("activate_project", {"project_path": project_path})

    # File Operations
    async def read_file(self, path: str) -> SerenaResponse:
        """Read file content."""
        return await self._call_tool("read_file", {"path": path})

    async def create_text_file(self, path: str, content: str) -> SerenaResponse:
        """Create a new text file."""
        return await self._call_tool(
            "create_text_file", {"path": path, "content": content}
        )

    async def list_dir(self, path: str) -> SerenaResponse:
        """List directory contents."""
        return await self._call_tool("list_dir", {"path": path})

    async def find_file(self, pattern: str, path: str | None = None) -> SerenaResponse:
        """Find files by pattern."""
        args = {"pattern": pattern}
        if path:
            args["path"] = path
        return await self._call_tool("find_file", args)

    # Symbol Operations
    async def get_symbols_overview(self, relative_path: str) -> SerenaResponse:
        """Get symbol overview for file."""
        return await self._call_tool(
            "get_symbols_overview", {"relative_path": relative_path}
        )

    async def find_symbol(
        self,
        name_path: str,
        relative_path: str | None = None,
        include_body: bool = False,
        depth: int | None = None,
    ) -> SerenaResponse:
        """Find specific symbols."""
        args = {"name_path": name_path, "include_body": include_body}
        if relative_path:
            args["relative_path"] = relative_path
        if depth is not None:
            args["depth"] = depth
        return await self._call_tool("find_symbol", args)

    async def find_referencing_symbols(
        self, name_path: str, relative_path: str | None = None
    ) -> SerenaResponse:
        """Find symbol references."""
        args = {"name_path": name_path}
        if relative_path:
            args["relative_path"] = relative_path
        return await self._call_tool("find_referencing_symbols", args)

    # Code Editing
    async def replace_regex(
        self,
        relative_path: str,
        pattern: str,
        replacement: str,
        allow_multiple_occurrences: bool = False,
    ) -> SerenaResponse:
        """Replace text using regex."""
        return await self._call_tool(
            "replace_regex",
            {
                "relative_path": relative_path,
                "pattern": pattern,
                "replacement": replacement,
                "allow_multiple_occurrences": allow_multiple_occurrences,
            },
        )

    async def replace_symbol_body(
        self, name_path: str, new_body: str, relative_path: str | None = None
    ) -> SerenaResponse:
        """Replace symbol implementation."""
        args = {"name_path": name_path, "new_body": new_body}
        if relative_path:
            args["relative_path"] = relative_path
        return await self._call_tool("replace_symbol_body", args)

    async def insert_after_symbol(
        self, name_path: str, content: str, relative_path: str | None = None
    ) -> SerenaResponse:
        """Insert code after symbol."""
        args = {"name_path": name_path, "content": content}
        if relative_path:
            args["relative_path"] = relative_path
        return await self._call_tool("insert_after_symbol", args)

    async def insert_before_symbol(
        self, name_path: str, content: str, relative_path: str | None = None
    ) -> SerenaResponse:
        """Insert code before symbol."""
        args = {"name_path": name_path, "content": content}
        if relative_path:
            args["relative_path"] = relative_path
        return await self._call_tool("insert_before_symbol", args)

    # Search Operations
    async def search_for_pattern(
        self, pattern: str, relative_path: str | None = None
    ) -> SerenaResponse:
        """Search for patterns in code."""
        args = {"pattern": pattern}
        if relative_path:
            args["relative_path"] = relative_path
        return await self._call_tool("search_for_pattern", args)

    # Memory Operations
    async def write_memory(self, key: str, value: str) -> SerenaResponse:
        """Write to agent memory."""
        return await self._call_tool("write_memory", {"key": key, "value": value})

    async def read_memory(self, key: str) -> SerenaResponse:
        """Read from agent memory."""
        return await self._call_tool("read_memory", {"key": key})

    async def list_memories(self) -> SerenaResponse:
        """List stored memories."""
        return await self._call_tool("list_memories", {})

    async def delete_memory(self, key: str) -> SerenaResponse:
        """Delete memory."""
        return await self._call_tool("delete_memory", {"key": key})

    # System Operations
    async def execute_shell_command(self, command: str) -> SerenaResponse:
        """Execute shell command."""
        return await self._call_tool("execute_shell_command", {"command": command})

    # Project Onboarding
    async def check_onboarding_performed(self) -> SerenaResponse:
        """Check onboarding status."""
        return await self._call_tool("check_onboarding_performed", {})

    async def onboarding(self) -> SerenaResponse:
        """Perform project onboarding."""
        return await self._call_tool("onboarding", {})

    # Analysis Tools
    async def think_about_collected_information(self) -> SerenaResponse:
        """Process collected information."""
        return await self._call_tool("think_about_collected_information", {})

    async def think_about_task_adherence(self) -> SerenaResponse:
        """Check task adherence."""
        return await self._call_tool("think_about_task_adherence", {})

    async def think_about_whether_you_are_done(self) -> SerenaResponse:
        """Check completion status."""
        return await self._call_tool("think_about_whether_you_are_done", {})

    async def prepare_for_new_conversation(self) -> SerenaResponse:
        """Prepare for new session."""
        return await self._call_tool("prepare_for_new_conversation", {})

    # Utility Methods
    async def health_check(self) -> bool:
        """Check if Serena MCP server is healthy."""
        try:
            # Try to list tools as a health check
            if not self._connected:
                connected = await self.connect()
                return connected
            return True
        except Exception:
            return False

    async def list_tools(self) -> SerenaResponse:
        """List available tools."""
        if not self._connected or not self.session:
            connected = await self.connect()
            if not connected:
                return SerenaResponse(
                    success=False, error="Not connected to MCP server"
                )

        try:
            result = await self.session.list_tools()
            tools_data = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in result.tools
            ]
            return SerenaResponse(success=True, data=tools_data)
        except Exception as e:
            return SerenaResponse(success=False, error=str(e))

    def get_supported_languages(self) -> list[SerenaLanguage]:
        """Get list of supported languages."""
        return list(SerenaLanguage)

    # Context Building Helpers
    async def build_file_context(self, file_path: str) -> dict[str, Any]:
        """Build comprehensive context for a file."""
        context = {
            "file_path": file_path,
            "content": None,
            "symbols": None,
            "errors": [],
        }

        # Get file content
        content_resp = await self.read_file(file_path)
        if content_resp.success:
            context["content"] = content_resp.data
        else:
            context["errors"].append(f"Failed to read file: {content_resp.error}")

        # Get symbols
        symbols_resp = await self.get_symbols_overview(file_path)
        if symbols_resp.success:
            context["symbols"] = symbols_resp.data
        else:
            context["errors"].append(f"Failed to get symbols: {symbols_resp.error}")

        return context

    async def build_project_context(self, workspace_path: str) -> dict[str, Any]:
        """Build comprehensive context for a project."""
        context = {
            "workspace_path": workspace_path,
            "activated": False,
            "files": None,
            "errors": [],
        }

        # Activate project
        activate_resp = await self.activate_project(workspace_path)
        if activate_resp.success:
            context["activated"] = True
        else:
            context["errors"].append(
                f"Failed to activate project: {activate_resp.error}"
            )

        # List files
        files_resp = await self.list_dir(workspace_path)
        if files_resp.success:
            context["files"] = files_resp.data
        else:
            context["errors"].append(f"Failed to list files: {files_resp.error}")

        return context

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
