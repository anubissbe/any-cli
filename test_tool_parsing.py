#!/usr/bin/env python3
"""Test script to debug tool parsing issue in interactive CLI."""

import asyncio
import re
import json
from plato.core.embedded_tools import ToolManager

async def test_xml_tool_parsing():
    """Test parsing of XML-style tool calls."""
    print("🧪 Testing Tool Call Parsing\n")
    print("=" * 50)
    
    # Sample AI response with tool call
    test_message = """I'll help you create a hello world Python file.

<tool_call>
<function=WriteFileTool>
<parameter=file_path>hello.py</parameter>
<parameter=content>print("Hello, World!")</parameter>
</function>
</tool_call>

The file has been created with a simple hello world program."""

    print("Test Message:")
    print(test_message)
    print("\n" + "=" * 50)
    
    # Parse tool calls using the same logic as interactive_cli.py
    tool_calls = []
    
    # Pattern for XML-style tool calls
    pattern = r"<tool_call>(.*?)</tool_call>"
    matches = re.findall(pattern, test_message, re.DOTALL)
    
    for match in matches:
        tool_content = match
        print(f"\nFound tool_call content:\n{tool_content}")
        
        # Extract function name
        func_match = re.search(r"<function=([^>]+)>", tool_content)
        if not func_match:
            print("  ❌ No function found")
            continue
        tool_name = func_match.group(1)
        print(f"  ✓ Tool name: {tool_name}")
        
        # Extract parameters
        param_pattern = r"<parameter=([^>]+)>([^<]*)</parameter>"
        param_matches = re.findall(param_pattern, tool_content)
        
        # Fallback for parameters without closing tags
        if not param_matches:
            param_pattern = r"<parameter=([^>]+)>([^<]*)"
            param_matches = re.findall(param_pattern, tool_content)
        
        params = {}
        for param_name, param_value in param_matches:
            params[param_name] = param_value.strip()
            print(f"  ✓ Parameter: {param_name} = {param_value.strip()}")
        
        tool_calls.append({"tool": tool_name, "parameters": params})
    
    print("\n" + "=" * 50)
    print(f"\nParsed {len(tool_calls)} tool calls:")
    for i, call in enumerate(tool_calls):
        print(f"\n{i+1}. {json.dumps(call, indent=2)}")
    
    # Now test execution
    if tool_calls:
        print("\n" + "=" * 50)
        print("\n🔧 Testing Tool Execution:")
        
        tool_manager = ToolManager()
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            
            print(f"\nExecuting: {tool_name}")
            print(f"Parameters: {parameters}")
            
            try:
                result = await tool_manager.execute_tool(tool_name, **parameters)
                print(f"Result: {'✅ Success' if result.success else '❌ Failed'}")
                if result.error:
                    print(f"Error: {result.error}")
                if result.data:
                    print(f"Data: {result.data}")
            except Exception as e:
                print(f"Exception: {e}")
    
    print("\n" + "=" * 50)
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_xml_tool_parsing())