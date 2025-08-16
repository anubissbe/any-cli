#!/usr/bin/env python3
"""Test that the CLI properly executes tool calls from AI responses."""

import asyncio
import json
from pathlib import Path
from plato.interactive_cli import PlatoInteractiveCLI

async def test_tool_execution():
    """Test that tool calls are properly executed."""
    
    # Create a mock CLI instance
    cli = PlatoInteractiveCLI()
    
    # Test response with tool call
    test_response = """I'll create a hello.py file for you.
<tool_call>
<function=WriteFileTool>
<parameter=file_path>/tmp/test_hello.py</parameter>
<parameter=content>print("Hello, World!")</parameter>
</function>
</tool_call>"""
    
    # Process the response
    await cli._handle_ai_tool_requests(test_response)
    
    # Check if file was created
    test_file = Path("/tmp/test_hello.py")
    if test_file.exists():
        content = test_file.read_text()
        if content == 'print("Hello, World!")':
            print("✅ SUCCESS: Tool call was executed and file was created with correct content!")
        else:
            print(f"❌ FAIL: File created but content is wrong: {content}")
        # Clean up
        test_file.unlink()
    else:
        print("❌ FAIL: Tool call was not executed - file not created")

if __name__ == "__main__":
    asyncio.run(test_tool_execution())