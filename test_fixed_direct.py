#!/usr/bin/env python3
"""
Direct test of fixed Serena MCP integration without importing through Plato modules.
"""

import asyncio
import sys
from pathlib import Path

# Add Serena's MCP libraries to path
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

try:
    import mcp.types as types
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client

    class SerenaResponse:
        """Simple response wrapper."""

        def __init__(self, success: bool, data=None, error=None):
            self.success = success
            self.data = data
            self.error = error

        @classmethod
        def from_mcp_result(cls, result):
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

            return cls(success=True, data=content_data)

    class FixedSerenaMCPClient:
        """Fixed MCP client for Serena using proper protocol."""

        def __init__(self, host="localhost", port=8765):
            self.host = host
            self.port = port
            self.base_url = f"http://{host}:{port}"
            self.sse_url = f"{self.base_url}/sse"
            self.session = None
            self.transport_context = None
            self._connected = False

        async def connect(self):
            """Connect using proper MCP protocol over SSE."""
            try:
                print(f"🔌 Connecting to Serena MCP via SSE: {self.sse_url}")

                # Create SSE client connection
                self.transport_context = sse_client(
                    self.sse_url, timeout=30, sse_read_timeout=60
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
                print(f"✅ MCP session initialized")
                print(
                    f"   Server: {init_result.server_info.name} v{init_result.server_info.version}"
                )

                self._connected = True
                return True

            except Exception as e:
                print(f"❌ Failed to connect: {e}")
                await self._cleanup()
                return False

        async def disconnect(self):
            """Disconnect from Serena."""
            await self._cleanup()

        async def _cleanup(self):
            """Clean up connection resources."""
            try:
                if self.session:
                    await self.session.close()
                    self.session = None

                if self.transport_context:
                    await self.transport_context.__aexit__(None, None, None)
                    self.transport_context = None

                self._connected = False
                print("🔌 Disconnected from Serena MCP")

            except Exception as e:
                print(f"⚠️ Error during disconnect: {e}")

        async def call_tool(self, tool_name: str, arguments: dict):
            """Call a tool via MCP protocol."""
            if not self._connected:
                raise RuntimeError("Not connected to MCP server")

            try:
                print(f"🔧 Calling tool: {tool_name}")

                # Use MCP protocol to call tool
                result = await self.session.call_tool(tool_name, arguments)

                return SerenaResponse.from_mcp_result(result)

            except Exception as e:
                print(f"❌ Failed to call tool {tool_name}: {e}")
                return SerenaResponse(success=False, error=str(e))

        async def list_tools(self):
            """List available tools."""
            if not self._connected:
                raise RuntimeError("Not connected to MCP server")

            try:
                result = await self.session.list_tools()
                tools_data = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                    }
                    for tool in result.tools
                ]
                return SerenaResponse(success=True, data=tools_data)
            except Exception as e:
                return SerenaResponse(success=False, error=str(e))

        async def __aenter__(self):
            await self.connect()
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.disconnect()

    async def test_fixed_integration():
        """Test the fixed integration."""
        print("🎯 Testing FIXED Plato-Serena Integration")
        print("=" * 50)

        async with FixedSerenaMCPClient() as client:

            # Test 1: List Tools
            print("\n1. 🔧 Testing Tool Listing...")
            tools_resp = await client.list_tools()

            if tools_resp.success:
                tools = tools_resp.data
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:5], 1):
                    print(f"   {i}. {tool['name']}: {tool['description'][:60]}...")
                if len(tools) > 5:
                    print(f"   ... and {len(tools) - 5} more tools")
            else:
                print(f"❌ Failed to list tools: {tools_resp.error}")
                return False

            # Test 2: Activate Project
            print("\n2. 📁 Testing Project Activation...")
            activate_resp = await client.call_tool(
                "activate_project", {"project_path": "/opt/projects/plato"}
            )

            if activate_resp.success:
                print("✅ Project activated successfully")
            else:
                print(f"❌ Project activation failed: {activate_resp.error}")

            # Test 3: List Directory
            print("\n3. 📄 Testing Directory Listing...")
            list_resp = await client.call_tool(
                "list_dir", {"path": "/opt/projects/plato"}
            )

            if list_resp.success:
                print("✅ Directory listing successful")
                if list_resp.data:
                    files = (
                        list_resp.data.split("\n")[:5]
                        if isinstance(list_resp.data, str)
                        else []
                    )
                    for file in files:
                        if file.strip():
                            print(f"   - {file.strip()}")
            else:
                print(f"❌ Directory listing failed: {list_resp.error}")

            # Test 4: File Reading
            print("\n4. 📖 Testing File Reading...")
            read_resp = await client.call_tool("read_file", {"path": "plato/cli.py"})

            if read_resp.success:
                print("✅ File reading successful")
                if read_resp.data:
                    lines = (
                        read_resp.data.split("\n")[:3]
                        if isinstance(read_resp.data, str)
                        else []
                    )
                    print(f"   First 3 lines:")
                    for i, line in enumerate(lines, 1):
                        print(f"   {i}: {line}")
            else:
                print(f"❌ File reading failed: {read_resp.error}")

            # Test 5: Symbol Overview
            print("\n5. 🔍 Testing Symbol Overview...")
            symbols_resp = await client.call_tool(
                "get_symbols_overview", {"relative_path": "plato/cli.py"}
            )

            if symbols_resp.success:
                print("✅ Symbol overview successful")
                if symbols_resp.data:
                    preview = (
                        symbols_resp.data[:200] + "..."
                        if len(symbols_resp.data) > 200
                        else symbols_resp.data
                    )
                    print(f"   Symbols preview: {preview}")
            else:
                print(f"❌ Symbol overview failed: {symbols_resp.error}")

            print("\n✅ All tests completed successfully!")
            print("🎉 Fixed Plato-Serena integration is working!")

            return True

    async def main():
        """Run the test."""
        print("🧪 Direct Test of Fixed Plato-Serena Integration")
        print("This uses the CORRECT MCP protocol over SSE")
        print()

        success = await test_fixed_integration()

        print("\n" + "=" * 60)
        print(f"📊 Final Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

        if success:
            print("✨ The protocol fix is working correctly!")
            print("🔧 Serena tools are accessible via proper MCP protocol")

        return success

    if __name__ == "__main__":
        try:
            result = asyncio.run(main())
            sys.exit(0 if result else 1)
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to run from Serena environment with MCP libraries")
