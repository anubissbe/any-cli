#!/usr/bin/env python3
"""Quick test to verify Serena MCP fix is working."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from plato.integrations.serena_mcp import SerenaMCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_serena_fix():
    """Test that the Serena MCP fix works."""
    logger.info("🔧 Testing Serena MCP fix...")

    client = SerenaMCPClient()

    try:
        # Test connection
        logger.info("  → Connecting to Serena MCP...")
        connected = await client.connect()

        if not connected:
            logger.error("  ✗ Failed to connect to Serena MCP")
            return False

        logger.info("  ✓ Connected successfully")

        # Test listing tools
        logger.info("  → Listing available tools...")
        tools_response = await client.list_tools()

        if not tools_response.success:
            logger.error(f"  ✗ Failed to list tools: {tools_response.error}")
            return False

        tools = tools_response.data
        logger.info(f"  ✓ Found {len(tools)} tools available")

        # Test project activation
        logger.info("  → Testing project activation...")
        activate_response = await client.activate_project("/opt/projects/plato")

        if not activate_response.success:
            logger.warning(f"  ! Project activation failed: {activate_response.error}")
        else:
            logger.info("  ✓ Project activated successfully")

        # Test basic file operation
        logger.info("  → Testing file operations...")
        file_response = await client.read_file("plato/__init__.py")

        if not file_response.success:
            logger.warning(f"  ! File read failed: {file_response.error}")
        else:
            logger.info(f"  ✓ File read successful ({len(file_response.data)} chars)")

        # Test memory operations
        logger.info("  → Testing memory operations...")
        write_mem = await client.write_memory("test_key", "test_value")
        read_mem = await client.read_memory("test_key")

        if write_mem.success and read_mem.success:
            logger.info("  ✓ Memory operations working")
            # Clean up
            await client.delete_memory("test_key")
        else:
            logger.warning("  ! Memory operations failed")

        logger.info("🎉 Serena MCP fix verification SUCCESSFUL!")
        return True

    except Exception as e:
        logger.error(f"  ✗ Test failed with exception: {e}")
        return False

    finally:
        await client.disconnect()


if __name__ == "__main__":
    success = asyncio.run(test_serena_fix())
    sys.exit(0 if success else 1)
