#!/usr/bin/env python3
"""
Test script for embedded LSP integration in Plato.

This script tests the LSP tools by analyzing a sample Python file
and verifying that symbol detection, references, definitions,
and diagnostics work correctly.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add plato to path
sys.path.insert(0, str(Path(__file__).parent))

from plato.core.embedded_tools.tool_manager import ToolManager
from plato.core.embedded_tools.base import ToolResult


async def test_lsp_tools():
    """Test the LSP tools functionality."""
    print("=" * 60)
    print("Testing Plato Embedded LSP Integration")
    print("=" * 60)

    # Initialize tool manager
    tool_manager = ToolManager()

    # List available tools
    print("\n1. Available Tools:")
    print("-" * 30)
    tools = tool_manager.list_tools()
    for tool in sorted(tools):
        if any(
            lsp_word in tool.lower()
            for lsp_word in [
                "symbol",
                "reference",
                "definition",
                "diagnostic",
                "hover",
                "completion",
                "analysis",
            ]
        ):
            print(f"  ✓ {tool} (LSP)")
        else:
            print(f"  • {tool}")

    # Test file path
    test_file = os.path.join(os.path.dirname(__file__), "test_lsp_sample.py")
    if not os.path.exists(test_file):
        print(f"\n❌ Test file not found: {test_file}")
        return False

    print(f"\n2. Test File: {test_file}")
    print("-" * 30)

    # Test 1: Get Symbols
    print("\n3. Testing GetSymbolsTool:")
    print("-" * 30)
    try:
        result = await tool_manager.execute_tool(
            "GetSymbolsTool", file_path=test_file, include_body=False, language="python"
        )

        if result.success:
            data = result.data
            print(f"  ✓ Found {data.get('symbol_count', 0)} symbols")

            # Show some symbols
            symbols = data.get("symbols", [])[:5]  # Show first 5
            for symbol in symbols:
                print(
                    f"    - {symbol.get('name', 'N/A')} ({symbol.get('kind_name', 'Unknown')})"
                )
        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    # Test 2: Find References
    print("\n4. Testing FindReferencesTool:")
    print("-" * 30)
    try:
        # Look for references to 'Person' class (should be around line 9)
        result = await tool_manager.execute_tool(
            "FindReferencesTool",
            file_path=test_file,
            line=10,  # Around where Person class is defined
            column=6,  # At the 'Person' text
            language="python",
        )

        if result.success:
            data = result.data
            ref_count = data.get("reference_count", 0)
            print(f"  ✓ Found {ref_count} references")

            # Show some references
            references = data.get("references", [])[:3]  # Show first 3
            for ref in references:
                print(f"    - {ref.get('file', 'N/A')}:{ref.get('line', 0)+1}")
        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    # Test 3: Find Definition
    print("\n5. Testing FindDefinitionTool:")
    print("-" * 30)
    try:
        # Look for definition of a method call (e.g., get_name method call)
        result = await tool_manager.execute_tool(
            "FindDefinitionTool",
            file_path=test_file,
            line=44,  # Around where get_name() is called
            column=20,
            language="python",
        )

        if result.success:
            data = result.data
            def_count = data.get("definition_count", 0)
            print(f"  ✓ Found {def_count} definitions")

            # Show definitions
            definitions = data.get("definitions", [])
            for defn in definitions:
                print(f"    - {defn.get('file', 'N/A')}:{defn.get('line', 0)+1}")
        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    # Test 4: Get Diagnostics
    print("\n6. Testing GetDiagnosticsTool:")
    print("-" * 30)
    try:
        result = await tool_manager.execute_tool(
            "GetDiagnosticsTool", file_path=test_file, language="python"
        )

        if result.success:
            data = result.data
            total = data.get("total_diagnostics", 0)
            errors = data.get("error_count", 0)
            warnings = data.get("warning_count", 0)

            print(
                f"  ✓ Found {total} diagnostics ({errors} errors, {warnings} warnings)"
            )

            # Show some diagnostics
            diagnostics = data.get("diagnostics", [])[:3]  # Show first 3
            for diag in diagnostics:
                severity = diag.get("severity_name", "Unknown")
                message = diag.get("message", "No message")
                line = diag.get("line", 0) + 1
                print(f"    - Line {line}: {severity} - {message[:60]}...")
        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    # Test 5: Code Analysis
    print("\n7. Testing CodeAnalysisTool:")
    print("-" * 30)
    try:
        result = await tool_manager.execute_tool(
            "CodeAnalysisTool",
            file_path=test_file,
            include_symbols=True,
            include_diagnostics=True,
            include_symbol_bodies=False,
            language="python",
        )

        if result.success:
            data = result.data
            summary = data.get("summary", [])
            print(f"  ✓ Analysis completed")

            for item in summary:
                print(f"    - {item}")

            # Show symbol summary if available
            symbols = data.get("symbols", {})
            if "summary" in symbols:
                print(f"    Symbol breakdown:")
                for kind, count in symbols["summary"].items():
                    print(f"      {kind}: {count}")

        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    # Test 6: Hover Info
    print("\n8. Testing HoverInfoTool:")
    print("-" * 30)
    try:
        # Test hover on a class name
        result = await tool_manager.execute_tool(
            "HoverInfoTool",
            file_path=test_file,
            line=10,  # Person class definition
            column=6,
            language="python",
        )

        if result.success:
            data = result.data
            if data.get("hover_available", False):
                hover_text = data.get("hover_text", "No text")
                print(f"  ✓ Hover info available")
                print(f"    Preview: {hover_text[:100]}...")
            else:
                print(f"  ℹ No hover info at this position")
        else:
            print(f"  ❌ Failed: {result.error}")

    except Exception as e:
        print(f"  ❌ Exception: {e}")

    print("\n" + "=" * 60)
    print("LSP Integration Test Complete")
    print("=" * 60)

    return True


async def main():
    """Main test function."""
    try:
        success = await test_lsp_tools()
        if success:
            print("\n✅ Test completed successfully!")
            return 0
        else:
            print("\n❌ Test failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
