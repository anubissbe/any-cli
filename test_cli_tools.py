#!/usr/bin/env python3
"""Test tool execution in interactive CLI."""

import asyncio
import json
from unittest.mock import Mock, AsyncMock, MagicMock
from plato.interactive_cli import PlatoInteractiveCLI

async def test_cli_tool_handling():
    """Test that the CLI properly handles tool requests from AI responses."""
    
    # Create CLI instance
    cli = PlatoInteractiveCLI()
    cli.debug_mode = True  # Enable debug mode for more output
    
    # Mock console to capture output
    output_lines = []
    original_print = cli.console.print
    
    def capture_print(*args, **kwargs):
        output_lines.append(str(args[0]) if args else "")
        original_print(*args, **kwargs)
    
    cli.console.print = capture_print
    
    # Test 1: Response with XML-style tool call
    print("\n" + "="*60)
    print("TEST 1: XML-style tool call")
    print("="*60)
    
    response1 = {
        "message": """I'll create a hello world Python file for you.

<tool_call>
<function=WriteFileTool>
<parameter=file_path>test_hello.py</parameter>
<parameter=content>#!/usr/bin/env python3
print("Hello, World!")
print("This is a test file created by Plato CLI")</parameter>
</function>
</tool_call>

The file has been created successfully.""",
        "provider": "test",
        "tokens_used": 100,
        "session_id": "test-session",
        "metadata": {}
    }
    
    output_lines.clear()
    await cli._handle_ai_tool_requests(response1)
    
    # Check output
    found_tool_call = any("Found 1 tool call" in line for line in output_lines)
    executed_tool = any("Executing tool: WriteFileTool" in line for line in output_lines)
    
    print(f"✓ Found tool call message: {found_tool_call}")
    print(f"✓ Executed tool message: {executed_tool}")
    
    if not found_tool_call or not executed_tool:
        print("\n❌ FAILURE: Tool was not detected or executed!")
        print("\nCaptured output:")
        for line in output_lines[:10]:  # Show first 10 lines
            print(f"  {line}")
    else:
        print("✅ SUCCESS: Tool was detected and executed!")
    
    # Test 2: Response with JSON-style tool call
    print("\n" + "="*60)
    print("TEST 2: JSON-style tool call")
    print("="*60)
    
    response2 = {
        "message": """I'll read the file for you.

TOOL_CALL: {"tool": "ReadFileTool", "parameters": {"file_path": "test_hello.py"}}

Let me check the contents of that file.""",
        "provider": "test",
        "tokens_used": 50,
        "session_id": "test-session",
        "metadata": {}
    }
    
    output_lines.clear()
    await cli._handle_ai_tool_requests(response2)
    
    # Check output
    found_tool_call = any("Found 1 tool call" in line for line in output_lines)
    executed_tool = any("Executing tool: ReadFileTool" in line for line in output_lines)
    
    print(f"✓ Found tool call message: {found_tool_call}")
    print(f"✓ Executed tool message: {executed_tool}")
    
    if not found_tool_call or not executed_tool:
        print("\n❌ FAILURE: Tool was not detected or executed!")
        print("\nCaptured output:")
        for line in output_lines[:10]:
            print(f"  {line}")
    else:
        print("✅ SUCCESS: Tool was detected and executed!")
    
    # Test 3: Response with no tool calls
    print("\n" + "="*60)
    print("TEST 3: Response without tool calls")
    print("="*60)
    
    response3 = {
        "message": "This is just a regular response without any tool calls.",
        "provider": "test",
        "tokens_used": 20,
        "session_id": "test-session",
        "metadata": {}
    }
    
    output_lines.clear()
    await cli._handle_ai_tool_requests(response3)
    
    # Check output
    no_tools_found = any("No tool calls found" in line for line in output_lines)
    
    print(f"✓ No tools found message: {no_tools_found}")
    
    # Test 4: Multiple tool calls in one response
    print("\n" + "="*60)
    print("TEST 4: Multiple tool calls")
    print("="*60)
    
    response4 = {
        "message": """I'll create two files for you.

<tool_call>
<function=WriteFileTool>
<parameter=file_path>file1.txt</parameter>
<parameter=content>This is file 1</parameter>
</function>
</tool_call>

<tool_call>
<function=WriteFileTool>
<parameter=file_path>file2.txt</parameter>
<parameter=content>This is file 2</parameter>
</function>
</tool_call>

Both files have been created.""",
        "provider": "test",
        "tokens_used": 150,
        "session_id": "test-session",
        "metadata": {}
    }
    
    output_lines.clear()
    await cli._handle_ai_tool_requests(response4)
    
    # Check output
    found_multiple = any("Found 2 tool call" in line for line in output_lines)
    
    print(f"✓ Found multiple tool calls: {found_multiple}")
    
    if not found_multiple:
        print("\n❌ FAILURE: Multiple tools were not detected!")
        print("\nCaptured output:")
        for line in output_lines[:10]:
            print(f"  {line}")
    else:
        print("✅ SUCCESS: Multiple tools were detected!")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
    
    # Cleanup
    await cli.client.aclose()

if __name__ == "__main__":
    asyncio.run(test_cli_tool_handling())