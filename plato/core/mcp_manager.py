"""MCP Manager for connecting to and managing MCP servers."""

import asyncio
import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
import websockets
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MCPTransport(str, Enum):
    """MCP transport types."""

    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPToolType(str, Enum):
    """MCP tool types."""

    FUNCTION = "function"
    RESOURCE = "resource"
    PROMPT = "prompt"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    transport: MCPTransport
    command: list[str] | None = None
    url: str | None = None
    port: int | None = None
    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    env: dict[str, str] = field(default_factory=dict)
    args: dict[str, Any] = field(default_factory=dict)


class MCPTool(BaseModel):
    """MCP tool definition."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: dict[str, Any] = Field(..., description="JSON schema for tool inputs")
    server: str = Field(..., description="MCP server providing this tool")
    tool_type: MCPToolType = Field(MCPToolType.FUNCTION, description="Type of tool")


class MCPRequest(BaseModel):
    """MCP request message."""

    id: str = Field(..., description="Request ID")
    method: str = Field(..., description="MCP method name")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Request parameters"
    )


class MCPResponse(BaseModel):
    """MCP response message."""

    id: str = Field(..., description="Request ID")
    result: Any | None = Field(None, description="Response result")
    error: dict[str, Any] | None = Field(None, description="Error details")


class MCPConnection(ABC):
    """Abstract base class for MCP server connections."""

    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.connected = False
        self.tools: list[MCPTool] = []
        self.request_id = 0

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the MCP server."""
        pass

    @abstractmethod
    async def send_request(
        self, method: str, params: dict[str, Any] = None
    ) -> MCPResponse:
        """Send a request to the MCP server."""
        pass

    def get_next_id(self) -> str:
        """Get next request ID."""
        self.request_id += 1
        return str(self.request_id)

    async def list_tools(self) -> list[MCPTool]:
        """List available tools from the server."""
        if not self.connected:
            await self.connect()

        try:
            response = await self.send_request("tools/list")
            if response.error:
                raise Exception(f"Error listing tools: {response.error}")

            tools = []
            for tool_data in response.result.get("tools", []):
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    server=self.config.name,
                    tool_type=MCPToolType.FUNCTION,
                )
                tools.append(tool)

            self.tools = tools
            return tools

        except Exception as e:
            logger.error(f"Failed to list tools from {self.config.name}: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if not self.connected:
            await self.connect()

        try:
            response = await self.send_request(
                "tools/call", {"name": tool_name, "arguments": arguments}
            )

            if response.error:
                raise Exception(f"Tool call error: {response.error}")

            return response.result

        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {self.config.name}: {e}")
            raise


class STDIOMCPConnection(MCPConnection):
    """STDIO-based MCP connection."""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.process: subprocess.Popen | None = None
        self.pending_requests: dict[str, asyncio.Future] = {}
        self._read_task: asyncio.Task | None = None

    async def connect(self) -> bool:
        """Connect to STDIO MCP server."""
        if not self.config.command:
            raise ValueError("STDIO transport requires command")

        try:
            # Start the MCP server process
            env = {
                **asyncio.get_event_loop().run_in_executor(
                    None, lambda: dict(os.environ)
                ),
                **self.config.env,
            }
            self.process = await asyncio.create_subprocess_exec(
                *self.config.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Start reading responses
            self._read_task = asyncio.create_task(self._read_responses())

            # Send initialize request
            init_response = await self.send_request(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                    "clientInfo": {"name": "plato", "version": "0.1.0"},
                },
            )

            if init_response.error:
                raise Exception(f"Initialization failed: {init_response.error}")

            # Send initialized notification
            await self._send_notification("notifications/initialized")

            self.connected = True
            logger.info(f"Connected to STDIO MCP server: {self.config.name}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to connect to STDIO MCP server {self.config.name}: {e}"
            )
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from STDIO MCP server."""
        self.connected = False

        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except TimeoutError:
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")

        self.process = None

    async def send_request(
        self, method: str, params: dict[str, Any] = None
    ) -> MCPResponse:
        """Send request to STDIO MCP server."""
        if not self.process or not self.process.stdin:
            raise Exception("Not connected to MCP server")

        request_id = self.get_next_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        try:
            # Send request
            message = json.dumps(request) + "\n"
            self.process.stdin.write(message.encode())
            await self.process.stdin.drain()

            # Wait for response
            response_data = await asyncio.wait_for(future, timeout=self.config.timeout)
            return MCPResponse(
                id=request_id,
                result=response_data.get("result"),
                error=response_data.get("error"),
            )

        except TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise Exception(f"Request timeout for method {method}")
        except Exception:
            self.pending_requests.pop(request_id, None)
            raise

    async def _send_notification(self, method: str, params: dict[str, Any] = None):
        """Send notification to MCP server."""
        if not self.process or not self.process.stdin:
            return

        notification = {"jsonrpc": "2.0", "method": method, "params": params or {}}

        message = json.dumps(notification) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()

    async def _read_responses(self):
        """Read responses from MCP server."""
        if not self.process or not self.process.stdout:
            return

        try:
            while True:
                line = await self.process.stdout.readline()
                if not line:
                    break

                try:
                    response = json.loads(line.decode().strip())
                    if "id" in response and response["id"] in self.pending_requests:
                        future = self.pending_requests.pop(response["id"])
                        if not future.done():
                            future.set_result(response)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse MCP response: {e}")
                except Exception as e:
                    logger.error(f"Error processing MCP response: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error reading MCP responses: {e}")


class SSEMCPConnection(MCPConnection):
    """Server-Sent Events MCP connection."""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.client: httpx.AsyncClient | None = None
        self.base_url = self.config.url or f"http://localhost:{self.config.port}"

    async def connect(self) -> bool:
        """Connect to SSE MCP server."""
        try:
            self.client = httpx.AsyncClient(timeout=self.config.timeout)

            # Test connection with health check
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")

            self.connected = True
            logger.info(f"Connected to SSE MCP server: {self.config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to SSE MCP server {self.config.name}: {e}")
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from SSE MCP server."""
        self.connected = False
        if self.client:
            await self.client.aclose()
            self.client = None

    async def send_request(
        self, method: str, params: dict[str, Any] = None
    ) -> MCPResponse:
        """Send request to SSE MCP server."""
        if not self.client:
            raise Exception("Not connected to MCP server")

        request_id = self.get_next_id()

        try:
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": method,
                    "params": params or {},
                },
            )

            response.raise_for_status()
            data = response.json()

            return MCPResponse(
                id=request_id, result=data.get("result"), error=data.get("error")
            )

        except Exception as e:
            raise Exception(f"Request failed for method {method}: {e}")


class WebSocketMCPConnection(MCPConnection):
    """WebSocket MCP connection."""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.websocket: websockets.WebSocketServerProtocol | None = None
        self.pending_requests: dict[str, asyncio.Future] = {}
        self._read_task: asyncio.Task | None = None

    async def connect(self) -> bool:
        """Connect to WebSocket MCP server."""
        try:
            ws_url = self.config.url or f"ws://localhost:{self.config.port}/mcp"
            self.websocket = await websockets.connect(ws_url)

            # Start reading responses
            self._read_task = asyncio.create_task(self._read_responses())

            self.connected = True
            logger.info(f"Connected to WebSocket MCP server: {self.config.name}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to connect to WebSocket MCP server {self.config.name}: {e}"
            )
            await self.disconnect()
            return False

    async def disconnect(self):
        """Disconnect from WebSocket MCP server."""
        self.connected = False

        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def send_request(
        self, method: str, params: dict[str, Any] = None
    ) -> MCPResponse:
        """Send request to WebSocket MCP server."""
        if not self.websocket:
            raise Exception("Not connected to MCP server")

        request_id = self.get_next_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        try:
            # Send request
            await self.websocket.send(json.dumps(request))

            # Wait for response
            response_data = await asyncio.wait_for(future, timeout=self.config.timeout)
            return MCPResponse(
                id=request_id,
                result=response_data.get("result"),
                error=response_data.get("error"),
            )

        except TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise Exception(f"Request timeout for method {method}")
        except Exception:
            self.pending_requests.pop(request_id, None)
            raise

    async def _read_responses(self):
        """Read responses from WebSocket MCP server."""
        try:
            async for message in self.websocket:
                try:
                    response = json.loads(message)
                    if "id" in response and response["id"] in self.pending_requests:
                        future = self.pending_requests.pop(response["id"])
                        if not future.done():
                            future.set_result(response)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse WebSocket response: {e}")
                except Exception as e:
                    logger.error(f"Error processing WebSocket response: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error reading WebSocket responses: {e}")


class MCPManager:
    """Manager for MCP server connections and tools."""

    def __init__(self):
        self.servers: dict[str, MCPConnection] = {}
        self.tools: dict[str, MCPTool] = {}
        self._connection_lock = asyncio.Lock()

    def add_server(self, config: MCPServerConfig) -> bool:
        """Add an MCP server configuration."""
        if config.name in self.servers:
            logger.warning(f"Server {config.name} already exists")
            return False

        # Create appropriate connection type
        if config.transport == MCPTransport.STDIO:
            connection = STDIOMCPConnection(config)
        elif config.transport == MCPTransport.SSE:
            connection = SSEMCPConnection(config)
        elif config.transport == MCPTransport.WEBSOCKET:
            connection = WebSocketMCPConnection(config)
        else:
            raise ValueError(f"Unsupported transport: {config.transport}")

        self.servers[config.name] = connection
        logger.info(f"Added MCP server: {config.name} ({config.transport})")
        return True

    async def connect_all(self) -> dict[str, bool]:
        """Connect to all enabled MCP servers."""
        results = {}

        for name, connection in self.servers.items():
            if not connection.config.enabled:
                results[name] = False
                continue

            try:
                async with self._connection_lock:
                    success = await connection.connect()
                    results[name] = success

                    if success:
                        # Discover tools
                        tools = await connection.list_tools()
                        for tool in tools:
                            tool_key = f"{name}.{tool.name}"
                            self.tools[tool_key] = tool

                        logger.info(f"Discovered {len(tools)} tools from {name}")

            except Exception as e:
                logger.error(f"Failed to connect to {name}: {e}")
                results[name] = False

        return results

    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        for connection in self.servers.values():
            try:
                await connection.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from {connection.config.name}: {e}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the appropriate MCP server."""
        # Find tool and server
        tool = None
        server_name = None

        # Check if tool name includes server prefix
        if "." in tool_name:
            server_name, tool_name = tool_name.split(".", 1)
            tool_key = f"{server_name}.{tool_name}"
            tool = self.tools.get(tool_key)
        else:
            # Search all servers for tool
            for tool_key, t in self.tools.items():
                if t.name == tool_name:
                    tool = t
                    server_name = t.server
                    break

        if not tool or not server_name:
            raise ValueError(f"Tool not found: {tool_name}")

        connection = self.servers.get(server_name)
        if not connection:
            raise ValueError(f"Server not found: {server_name}")

        return await connection.call_tool(tool_name, arguments)

    def list_tools(self, server_name: str | None = None) -> list[MCPTool]:
        """List available tools, optionally filtered by server."""
        if server_name:
            return [tool for tool in self.tools.values() if tool.server == server_name]
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> MCPTool | None:
        """Get tool definition by name."""
        # Try with server prefix first
        if tool_name in self.tools:
            return self.tools[tool_name]

        # Search without prefix
        for tool in self.tools.values():
            if tool.name == tool_name:
                return tool

        return None

    def get_server_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all MCP servers."""
        status = {}

        for name, connection in self.servers.items():
            status[name] = {
                "connected": connection.connected,
                "transport": connection.config.transport.value,
                "enabled": connection.config.enabled,
                "tools_count": len(
                    [t for t in self.tools.values() if t.server == name]
                ),
            }

        return status

    @asynccontextmanager
    async def get_connection(
        self, server_name: str
    ) -> AsyncGenerator[MCPConnection, None]:
        """Get a connection to a specific MCP server."""
        connection = self.servers.get(server_name)
        if not connection:
            raise ValueError(f"Server not found: {server_name}")

        if not connection.connected:
            async with self._connection_lock:
                if not connection.connected:
                    await connection.connect()

        try:
            yield connection
        finally:
            # Optionally disconnect or keep alive
            pass
