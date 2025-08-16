#!/usr/bin/env python3
"""Test script for embedded tools in Plato."""

import asyncio
import json
from pathlib import Path

from plato.core.embedded_tools import ToolManager


async def test_embedded_tools():
    """Test the embedded tools functionality."""
    print("🧪 Testing Embedded Tools for Plato\n")
    print("=" * 50)

    # Initialize tool manager
    tool_manager = ToolManager()

    # List available tools
    print("\n📋 Available Tools:")
    for tool_name in tool_manager.list_tools():
        tool = tool_manager.get_tool(tool_name)
        print(f"  • {tool_name}: {tool.description}")

    print("\n" + "=" * 50)

    # Test 1: Create a test directory
    print("\n📁 Test 1: Create Directory")
    result = await tool_manager.execute_tool(
        "CreateDirectoryTool", directory_path="/tmp/plato_test"
    )
    print(f"  Result: {result.success}")
    if result.error:
        print(f"  Error: {result.error}")

    # Test 2: Write a test file
    print("\n📝 Test 2: Write File")
    test_content = """# Test File
This is a test file created by Plato's embedded tools.

## Features
- Line 1
- Line 2
- Line 3
"""
    result = await tool_manager.execute_tool(
        "WriteFileTool", file_path="/tmp/plato_test/test.md", content=test_content
    )
    print(f"  Result: {result.success}")
    if result.data:
        print(f"  Data: {result.data}")

    # Test 3: Read the file
    print("\n📖 Test 3: Read File")
    result = await tool_manager.execute_tool(
        "ReadFileTool", file_path="/tmp/plato_test/test.md"
    )
    print(f"  Result: {result.success}")
    if result.success:
        print("  Content (first 5 lines):")
        lines = result.data.split("\n")[:5]
        for line in lines:
            print(f"    {line}")

    # Test 4: Edit the file
    print("\n✏️  Test 4: Edit File")
    result = await tool_manager.execute_tool(
        "EditFileTool",
        file_path="/tmp/plato_test/test.md",
        old_content="- Line 2",
        new_content="- Line 2 (edited)",
    )
    print(f"  Result: {result.success}")
    if result.data:
        print(f"  Data: {result.data}")

    # Test 5: List directory
    print("\n📂 Test 5: List Directory")
    result = await tool_manager.execute_tool(
        "ListDirectoryTool", directory_path="/tmp/plato_test"
    )
    print(f"  Result: {result.success}")
    if result.success:
        print("  Contents:")
        for line in result.data.split("\n"):
            print(f"    {line}")

    # Test 6: Search in files
    print("\n🔍 Test 6: Search Files")
    result = await tool_manager.execute_tool(
        "SearchFilesTool", pattern="test", directory="/tmp/plato_test"
    )
    print(f"  Result: {result.success}")
    if result.data:
        print(f"  Search results:")
        lines = result.data.split("\n")[:3]
        for line in lines:
            print(f"    {line}")

    print("\n" + "=" * 50)
    print("\n✅ All tests completed!")

    # Test natural language parsing
    print("\n🗣️  Test 7: Natural Language Parsing")
    test_cases = [
        "read file /tmp/plato_test/test.md",
        "list directory /tmp",
        "search for 'test' in /tmp/plato_test",
    ]

    for test_text in test_cases:
        print(f"\n  Input: '{test_text}'")
        request = tool_manager.parse_tool_request(test_text)
        if request:
            print(f"  Parsed: {json.dumps(request, indent=2)}")
        else:
            print("  Could not parse request")

    print("\n" + "=" * 50)
    print("\n🎉 Embedded tools testing complete!")


if __name__ == "__main__":
    asyncio.run(test_embedded_tools())
