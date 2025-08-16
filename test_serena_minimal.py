#!/usr/bin/env python3
"""Minimal test for Serena MCP integration."""

import asyncio
import logging
import sys
from pathlib import Path

# Add Serena's MCP libraries to path
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

# Import MCP libraries directly
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerenaResponse:
    """Simple response wrapper."""

    def __init__(self, success: bool, data=None, error=None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def from_mcp_result(cls, result: types.CallToolResult):
        """Create response from MCP result."""
        if result.is_error:
            return cls(success=False, error=str(result.error))

        # Extract text content
        content_data = None
        if result.content:
            if len(result.content) == 1:
                content = result.content[0]
                content_data = getattr(content, "text", content)
            else:
                content_data = [getattr(c, "text", c) for c in result.content]

        return cls(success=True, data=content_data)


class MinimalSerenaMCPClient:
    """Minimal Serena MCP client for testing."""

    def __init__(self, host="localhost", port=8765, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sse_url = f"http://{host}:{port}/sse"

        self.session = None
        self.transport_context = None
        self._connected = False

    async def connect(self):
        """Connect to Serena MCP server."""
        try:
            logger.info(f"Connecting to Serena MCP: {self.sse_url}")

            # Create SSE connection
            self.transport_context = sse_client(
                self.sse_url, timeout=self.timeout, sse_read_timeout=60
            )

            read_stream, write_stream = await self.transport_context.__aenter__()

            # Create session
            self.session = ClientSession(
                read_stream=read_stream, write_stream=write_stream
            )

            # Initialize
            init_result = await self.session.initialize()
            logger.info(
                f"Connected: {init_result.server_info.name} v{init_result.server_info.version}"
            )

            self._connected = True
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect."""
        try:
            if self.session:
                await self.session.close()
            if self.transport_context:
                await self.transport_context.__aexit__(None, None, None)
            self._connected = False
        except Exception as e:
            logger.warning(f"Disconnect error: {e}")

    async def list_tools(self):
        """List available tools."""
        if not self._connected:
            return SerenaResponse(False, error="Not connected")

        try:
            result = await self.session.list_tools()
            tools_data = [
                {"name": tool.name, "description": tool.description}
                for tool in result.tools
            ]
            return SerenaResponse(True, tools_data)
        except Exception as e:
            return SerenaResponse(False, error=str(e))

    async def call_tool(self, tool_name, arguments):
        """Call a tool."""
        if not self._connected:
            return SerenaResponse(False, error="Not connected")

        try:
            result = await self.session.call_tool(tool_name, arguments)
            return SerenaResponse.from_mcp_result(result)
        except Exception as e:
            return SerenaResponse(False, error=str(e))


async def test_minimal_serena():
    """Test minimal Serena functionality."""
    logger.info("🧪 Testing minimal Serena MCP functionality...")

    client = MinimalSerenaMCPClient()

    try:
        # Test connection
        logger.info("→ Connecting...")
        connected = await client.connect()

        if not connected:
            logger.error("✗ Connection failed")
            return False

        logger.info("✓ Connected successfully")

        # Test tool listing
        logger.info("→ Listing tools...")
        tools_resp = await client.list_tools()

        if tools_resp.success:
            logger.info(f"✓ Found {len(tools_resp.data)} tools:")
            for tool in tools_resp.data[:5]:  # Show first 5
                logger.info(f"  - {tool['name']}: {tool['description'][:60]}...")
        else:
            logger.error(f"✗ Tool listing failed: {tools_resp.error}")
            return False

        # Test project activation
        logger.info("→ Testing project activation...")
        activate_resp = await client.call_tool(
            "activate_project", {"project_path": "/opt/projects/plato"}
        )

        if activate_resp.success:
            logger.info("✓ Project activation successful")
        else:
            logger.warning(f"! Project activation failed: {activate_resp.error}")

        # Test file reading
        logger.info("→ Testing file reading...")
        file_resp = await client.call_tool("read_file", {"path": "plato/__init__.py"})

        if file_resp.success and file_resp.data:
            logger.info(f"✓ File read successful ({len(file_resp.data)} chars)")
        else:
            logger.warning(f"! File read failed: {file_resp.error}")

        # Test directory listing
        logger.info("→ Testing directory listing...")
        dir_resp = await client.call_tool("list_dir", {"path": "."})

        if dir_resp.success:
            logger.info("✓ Directory listing successful")
        else:
            logger.warning(f"! Directory listing failed: {dir_resp.error}")

        # Test memory operations
        logger.info("→ Testing memory operations...")
        write_resp = await client.call_tool(
            "write_memory", {"key": "test", "value": "working"}
        )

        if write_resp.success:
            read_resp = await client.call_tool("read_memory", {"key": "test"})
            if read_resp.success and "working" in str(read_resp.data):
                logger.info("✓ Memory operations working")
                # Clean up
                await client.call_tool("delete_memory", {"key": "test"})
            else:
                logger.warning("! Memory read failed")
        else:
            logger.warning("! Memory write failed")

        logger.info("🎉 Minimal Serena MCP test SUCCESSFUL!")
        return True

    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        return False

    finally:
        await client.disconnect()


if __name__ == "__main__":
    success = asyncio.run(test_minimal_serena())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Minimal Serena MCP test")
    sys.exit(0 if success else 1)
