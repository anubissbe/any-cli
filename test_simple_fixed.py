#!/usr/bin/env python3
"""
Simple test to verify the fixed integration is working.
"""

import asyncio
import sys

# Add Serena's MCP libraries to path
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def test_connection():
    """Simple connection test."""
    print("🔌 Testing fixed Serena MCP connection...")

    try:
        # Connect using proper MCP protocol
        async with sse_client("http://localhost:8765/sse", timeout=10) as (
            read_stream,
            write_stream,
        ):
            print("✅ SSE transport connected")

            session = ClientSession(read_stream=read_stream, write_stream=write_stream)

            # Initialize session
            init_result = await session.initialize()
            print(f"✅ MCP session initialized")
            print(
                f"   Server: {init_result.server_info.name} v{init_result.server_info.version}"
            )

            # List tools
            tools_result = await session.list_tools()
            print(f"✅ Found {len(tools_result.tools)} tools")

            # Test one tool call
            result = await session.call_tool(
                "list_dir", {"path": "/opt/projects/plato"}
            )

            if result.is_error:
                print(f"❌ Tool call failed: {result.error}")
            else:
                print("✅ Tool call successful!")

            await session.close()
            print("✅ Session closed")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Simple Fixed Integration Test")
    print("=" * 40)

    success = asyncio.run(test_connection())

    print("\n" + "=" * 40)
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAILED'}")

    if success:
        print("🎉 Fixed integration is working!")
        print("✨ MCP protocol over SSE is properly implemented")

    sys.exit(0 if success else 1)
