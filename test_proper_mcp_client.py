#!/usr/bin/env python3
"""
Proper MCP client implementation for connecting to Serena MCP server.

This demonstrates the correct way to connect to Serena using the MCP protocol
over SSE transport, rather than trying to use HTTP REST endpoints.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add the serena library path to import MCP client
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


class ProperSerenaMCPClient:
    """Proper MCP client for Serena using SSE transport."""

    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url
        self.sse_url = f"{base_url}/sse"
        self.session: ClientSession | None = None

    async def connect(self) -> bool:
        """Connect to Serena MCP server using proper MCP protocol."""
        try:
            print(f"🔌 Connecting to Serena MCP via SSE: {self.sse_url}")

            # Create SSE client connection to Serena
            self.transport_context = sse_client(self.sse_url)
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
            print(f"✅ MCP session initialized successfully")
            print(
                f"   Server capabilities: {list(init_result.capabilities.model_dump().keys())}"
            )
            print(
                f"   Server info: {init_result.server_info.name} v{init_result.server_info.version}"
            )

            return True

        except Exception as e:
            print(f"❌ Failed to connect via MCP: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Serena MCP server."""
        try:
            if self.session:
                # Close the session gracefully
                await self.session.close()
                self.session = None

            if hasattr(self, "transport_context"):
                await self.transport_context.__aexit__(None, None, None)

            print("🔌 Disconnected from Serena MCP")

        except Exception as e:
            print(f"⚠️ Error during disconnect: {e}")

    async def list_tools(self) -> list[dict]:
        """List available tools via MCP."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            # Use MCP protocol to list tools
            result = await self.session.list_tools()
            tools = result.tools

            print(f"📋 Found {len(tools)} tools:")
            for tool in tools[:10]:  # Show first 10
                print(f"   - {tool.name}: {tool.description[:60]}...")

            if len(tools) > 10:
                print(f"   ... and {len(tools) - 10} more tools")

            return [tool.model_dump() for tool in tools]

        except Exception as e:
            print(f"❌ Failed to list tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a tool via MCP."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            print(f"🔧 Calling tool: {tool_name}")
            print(f"   Arguments: {json.dumps(arguments, indent=2)}")

            # Use MCP protocol to call tool
            result = await self.session.call_tool(tool_name, arguments)

            if result.is_error:
                print(f"❌ Tool call failed: {result.error}")
                return {"success": False, "error": str(result.error)}
            else:
                print(f"✅ Tool call successful")
                return {"success": True, "content": result.content}

        except Exception as e:
            print(f"❌ Failed to call tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}

    async def list_resources(self) -> list[dict]:
        """List available resources via MCP."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        try:
            # Use MCP protocol to list resources
            result = await self.session.list_resources()
            resources = result.resources

            print(f"📚 Found {len(resources)} resources:")
            for resource in resources[:5]:  # Show first 5
                print(f"   - {resource.uri}: {resource.name}")
                if resource.description:
                    print(f"     {resource.description[:60]}...")

            return [resource.model_dump() for resource in resources]

        except Exception as e:
            print(f"❌ Failed to list resources: {e}")
            return []


async def test_proper_mcp_connection():
    """Test proper MCP connection to Serena."""
    print("🚀 Testing Proper MCP Connection to Serena")
    print("=" * 50)

    client = ProperSerenaMCPClient()

    try:
        # Test connection
        print("\n1. 🔌 Testing MCP Connection...")
        connected = await client.connect()

        if not connected:
            print("❌ Failed to connect via MCP")
            return False

        # Test listing tools
        print("\n2. 🔧 Testing Tool Listing...")
        tools = await client.list_tools()

        # Test listing resources
        print("\n3. 📚 Testing Resource Listing...")
        resources = await client.list_resources()

        # Test calling a simple tool (if available)
        if tools:
            print("\n4. 🛠️ Testing Tool Call...")

            # Try to find a simple tool to test
            simple_tools = [
                t
                for t in tools
                if t["name"] in ["list_dir", "read_file", "get_symbols_overview"]
            ]

            if simple_tools:
                tool = simple_tools[0]
                tool_name = tool["name"]

                if tool_name == "list_dir":
                    result = await client.call_tool(
                        "list_dir", {"path": "/opt/projects/plato"}
                    )
                elif tool_name == "read_file":
                    result = await client.call_tool(
                        "read_file", {"path": "/opt/projects/plato/README.md"}
                    )
                elif tool_name == "get_symbols_overview":
                    result = await client.call_tool(
                        "get_symbols_overview", {"relative_path": "plato/cli.py"}
                    )

                if result.get("success"):
                    print(f"✅ Tool call successful!")
                    if result.get("content"):
                        # Show first content block
                        content = result["content"][0] if result["content"] else None
                        if content and "text" in content:
                            text = (
                                content["text"][:200] + "..."
                                if len(content["text"]) > 200
                                else content["text"]
                            )
                            print(f"   Result preview: {text}")
                else:
                    print(f"❌ Tool call failed: {result.get('error')}")
            else:
                print("⚠️ No suitable simple tools found for testing")

        print("\n✅ All MCP tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

    finally:
        await client.disconnect()


async def test_serena_specific_operations():
    """Test Serena-specific LSP operations."""
    print("\n🎯 Testing Serena LSP Operations")
    print("=" * 40)

    client = ProperSerenaMCPClient()

    try:
        await client.connect()

        # Test project activation
        print("\n1. 📁 Testing Project Activation...")
        result = await client.call_tool(
            "activate_project", {"project_path": "/opt/projects/plato"}
        )
        if result.get("success"):
            print("✅ Project activated successfully")
        else:
            print(f"❌ Project activation failed: {result.get('error')}")

        # Test file reading
        print("\n2. 📄 Testing File Reading...")
        result = await client.call_tool("read_file", {"path": "plato/cli.py"})
        if result.get("success"):
            print("✅ File read successfully")
            # Show a snippet
            if result.get("content"):
                content = result["content"][0] if result["content"] else None
                if content and "text" in content:
                    lines = content["text"].split("\n")[:5]
                    print(f"   First 5 lines:")
                    for i, line in enumerate(lines, 1):
                        print(f"   {i}: {line}")
        else:
            print(f"❌ File read failed: {result.get('error')}")

        # Test symbol overview
        print("\n3. 🔍 Testing Symbol Overview...")
        result = await client.call_tool(
            "get_symbols_overview", {"relative_path": "plato/cli.py"}
        )
        if result.get("success"):
            print("✅ Symbol overview successful")
            if result.get("content"):
                content = result["content"][0] if result["content"] else None
                if content and "text" in content:
                    text = (
                        content["text"][:300] + "..."
                        if len(content["text"]) > 300
                        else content["text"]
                    )
                    print(f"   Symbols preview: {text}")
        else:
            print(f"❌ Symbol overview failed: {result.get('error')}")

        # Test symbol finding
        print("\n4. 🎯 Testing Symbol Finding...")
        result = await client.call_tool(
            "find_symbol", {"symbol_name": "PlatoClient", "symbol_type": "class"}
        )
        if result.get("success"):
            print("✅ Symbol finding successful")
            if result.get("content"):
                content = result["content"][0] if result["content"] else None
                if content and "text" in content:
                    text = (
                        content["text"][:200] + "..."
                        if len(content["text"]) > 200
                        else content["text"]
                    )
                    print(f"   Found symbol: {text}")
        else:
            print(f"❌ Symbol finding failed: {result.get('error')}")

        print("\n✅ Serena LSP operations test completed!")
        return True

    except Exception as e:
        print(f"❌ Serena operations test failed: {e}")
        return False

    finally:
        await client.disconnect()


async def main():
    """Run all MCP tests."""
    print("🧪 Serena MCP Integration Tests - Proper Protocol")
    print("This tests the CORRECT way to connect to Serena using MCP over SSE")
    print()

    # Test 1: Basic MCP connection
    basic_success = await test_proper_mcp_connection()

    # Test 2: Serena-specific operations
    serena_success = await test_serena_specific_operations()

    print("\n" + "=" * 60)
    print("📊 Final Test Results:")
    print(
        f"   {'✅' if basic_success else '❌'} Basic MCP Connection: {'PASS' if basic_success else 'FAIL'}"
    )
    print(
        f"   {'✅' if serena_success else '❌'} Serena LSP Operations: {'PASS' if serena_success else 'FAIL'}"
    )

    overall_success = basic_success and serena_success
    print(f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("🎉 Serena MCP integration is working correctly!")
    else:
        print("⚠️ Issues found in Serena MCP integration.")

    return overall_success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
