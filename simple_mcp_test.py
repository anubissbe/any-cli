#!/usr/bin/env python3
"""
Simple MCP connection test to verify Serena integration.
"""

import asyncio
import sys
import json

# Use the Serena repo's venv for MCP libraries
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

try:
    import mcp.types as types
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client

    async def test_connection():
        print("🔌 Testing MCP SSE connection to Serena...")

        sse_url = "http://localhost:8765/sse"
        print(f"   Connecting to: {sse_url}")

        try:
            # Create SSE transport
            async with sse_client(sse_url, timeout=10, sse_read_timeout=30) as (
                read_stream,
                write_stream,
            ):
                print("✅ SSE transport connected")

                # Create MCP session
                session = ClientSession(
                    read_stream=read_stream, write_stream=write_stream
                )

                # Initialize session
                print("🤝 Initializing MCP session...")
                init_result = await session.initialize()

                print("✅ MCP session initialized!")
                print(
                    f"   Server: {init_result.server_info.name} v{init_result.server_info.version}"
                )

                # List tools
                print("\n🔧 Listing available tools...")
                tools_result = await session.list_tools()
                tools = tools_result.tools

                print(f"   Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:5]):  # Show first 5
                    print(f"   {i+1}. {tool.name}")

                if len(tools) > 5:
                    print(f"   ... and {len(tools) - 5} more")

                # Try calling a simple tool
                print("\n🛠️  Testing tool call...")

                # Find a safe tool to test
                safe_tools = ["list_dir", "read_file", "get_symbols_overview"]
                test_tool = None

                for tool in tools:
                    if tool.name in safe_tools:
                        test_tool = tool
                        break

                if test_tool:
                    print(f"   Calling tool: {test_tool.name}")

                    if test_tool.name == "list_dir":
                        args = {"path": "/opt/projects/plato"}
                    elif test_tool.name == "read_file":
                        args = {"path": "plato/README.md"}
                    else:  # get_symbols_overview
                        args = {"relative_path": "plato/cli.py"}

                    try:
                        result = await session.call_tool(test_tool.name, args)

                        if result.is_error:
                            print(f"   ❌ Tool call failed: {result.error}")
                        else:
                            print("   ✅ Tool call successful!")
                            if result.content:
                                content = result.content[0]
                                if hasattr(content, "text"):
                                    preview = (
                                        content.text[:100] + "..."
                                        if len(content.text) > 100
                                        else content.text
                                    )
                                    print(f"   Result preview: {preview}")

                    except Exception as e:
                        print(f"   ❌ Tool call error: {e}")

                else:
                    print("   ⚠️  No safe tools found for testing")

                # Close session
                await session.close()
                print("\n✅ MCP session closed successfully")

                return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    async def main():
        print("🧪 Simple Serena MCP Connection Test")
        print("=" * 40)

        success = await test_connection()

        print("\n" + "=" * 40)
        print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

        if success:
            print("🎉 Serena MCP integration is working!")
        else:
            print("⚠️  Connection issues detected")

        return success

    if __name__ == "__main__":
        try:
            result = asyncio.run(main())
            print(f"\nExit code: {0 if result else 1}")
        except Exception as e:
            print(f"❌ Test failed: {e}")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure MCP libraries are available")
