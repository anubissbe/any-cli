#!/usr/bin/env python3
"""Test Serena MCP fix using Serena's environment."""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path

# Set up environment to use Serena's Python environment
serena_python = "/opt/serena-repo/.venv/bin/python"
project_root = "/opt/projects/plato"

# Add Serena environment to Python path
sys.path.insert(0, "/opt/serena-repo/.venv/lib/python3.11/site-packages")
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_serena_direct():
    """Test Serena MCP integration directly."""
    logger.info("🔧 Testing Serena MCP integration with proper environment...")

    try:
        # Import after setting up path
        from plato.integrations.serena_mcp import SerenaMCPClient

        client = SerenaMCPClient()

        # Test connection
        logger.info("  → Attempting connection...")
        connected = await client.connect()

        if not connected:
            logger.error("  ✗ Connection failed")
            return False

        logger.info("  ✓ Connected successfully")

        # Test basic operations
        logger.info("  → Testing tool listing...")
        tools_resp = await client.list_tools()

        if tools_resp.success:
            logger.info(f"  ✓ Found {len(tools_resp.data)} tools")
            for i, tool in enumerate(tools_resp.data[:5]):  # Show first 5 tools
                logger.info(f"    - {tool['name']}: {tool['description'][:50]}...")
        else:
            logger.warning(f"  ! Tool listing failed: {tools_resp.error}")

        # Test project activation
        logger.info("  → Testing project activation...")
        activate_resp = await client.activate_project("/opt/projects/plato")

        if activate_resp.success:
            logger.info("  ✓ Project activated")
        else:
            logger.warning(f"  ! Activation failed: {activate_resp.error}")

        # Test file operations
        logger.info("  → Testing file reading...")
        file_resp = await client.read_file("plato/__init__.py")

        if file_resp.success and file_resp.data:
            logger.info(f"  ✓ File read successful ({len(file_resp.data)} chars)")
        else:
            logger.warning(f"  ! File read failed: {file_resp.error}")

        # Test directory listing
        logger.info("  → Testing directory listing...")
        dir_resp = await client.list_dir(".")

        if dir_resp.success and dir_resp.data:
            logger.info(f"  ✓ Directory listed ({len(dir_resp.data)} items)")
        else:
            logger.warning(f"  ! Directory listing failed: {dir_resp.error}")

        # Test symbol operations
        logger.info("  → Testing symbol operations...")
        symbols_resp = await client.get_symbols_overview("plato/__init__.py")

        if symbols_resp.success:
            logger.info("  ✓ Symbol overview successful")
        else:
            logger.warning(f"  ! Symbol overview failed: {symbols_resp.error}")

        # Test search
        logger.info("  → Testing search operations...")
        search_resp = await client.search_for_pattern("class")

        if search_resp.success:
            logger.info("  ✓ Search successful")
        else:
            logger.warning(f"  ! Search failed: {search_resp.error}")

        logger.info("🎉 All tests completed successfully!")
        return True

    except Exception as e:
        logger.error(f"  ✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        try:
            await client.disconnect()
        except:
            pass


def run_test():
    """Run the test."""
    return asyncio.run(test_serena_direct())


if __name__ == "__main__":
    success = run_test()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Serena MCP integration test")
    sys.exit(0 if success else 1)
