#!/usr/bin/env python3
"""
Demo script showing Plato's embedded LSP capabilities.

This script demonstrates the various LSP tools available in Plato,
showing how they can analyze Python code even without external
language server dependencies.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add plato to path
sys.path.insert(0, str(Path(__file__).parent))

from plato.core.embedded_tools.tool_manager import ToolManager


async def demo_lsp_capabilities():
    """Demonstrate LSP capabilities with a real example."""
    print("🔍 Plato Embedded LSP Capabilities Demo")
    print("=" * 50)

    # Initialize tool manager
    tool_manager = ToolManager()

    # Test file
    test_file = os.path.join(os.path.dirname(__file__), "test_lsp_sample.py")

    print(f"\n📁 Analyzing file: {os.path.basename(test_file)}")
    print("-" * 50)

    # Demo 1: Get comprehensive code analysis
    print("\n1️⃣ Comprehensive Code Analysis")
    print("-" * 30)

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
        print("📊 Analysis Summary:")
        for item in data.get("summary", []):
            print(f"   • {item}")

        print("\n🔧 Symbol Breakdown:")
        symbols = data.get("symbols", {})
        if "summary" in symbols:
            for kind, count in symbols["summary"].items():
                print(f"   • {kind}: {count}")

        print("\n📋 Detailed Symbols:")
        symbol_categories = symbols.get("categories", {})
        for category, items in symbol_categories.items():
            if items:
                print(f"   {category}:")
                for item in items[:3]:  # Show first 3
                    line = item.get("line", 0) + 1
                    name = item.get("name", "N/A")
                    print(f"     - {name} (line {line})")
                if len(items) > 3:
                    print(f"     ... and {len(items) - 3} more")

    # Demo 2: Get detailed symbols with source code
    print("\n2️⃣ Symbol Detection with Source Code")
    print("-" * 30)

    result = await tool_manager.execute_tool(
        "GetSymbolsTool", file_path=test_file, include_body=True, language="python"
    )

    if result.success:
        data = result.data
        symbols = data.get("symbols", [])

        print(f"🎯 Found {len(symbols)} symbols with source code:")

        # Show a few interesting symbols
        for symbol in symbols[:3]:
            name = symbol.get("name", "N/A")
            kind = symbol.get("kind_name", "Unknown")
            range_info = symbol.get("range", {})
            start_line = range_info.get("start", {}).get("line", 0) + 1

            print(f"\n   📌 {name} ({kind}) - Line {start_line}")

            # Show source code if available
            if "body" in symbol:
                body = symbol["body"]
                lines = body.split("\n")
                for i, line in enumerate(lines[:4]):  # Show first 4 lines
                    print(f"      {start_line + i:3d}: {line}")
                if len(lines) > 4:
                    print(f"      ... ({len(lines) - 4} more lines)")

    # Demo 3: Find references to a specific symbol
    print("\n3️⃣ Reference Finding")
    print("-" * 30)

    # Try to find references to 'Person' (around line 10, column 6)
    result = await tool_manager.execute_tool(
        "FindReferencesTool",
        file_path=test_file,
        line=10,  # Person class definition
        column=6,
        language="python",
    )

    if result.success:
        data = result.data
        ref_count = data.get("reference_count", 0)
        print(f"🔗 Found {ref_count} references to symbol at line 11, column 7")

        references = data.get("references", [])
        for ref in references[:5]:  # Show first 5
            line = ref.get("line", 0) + 1
            file_name = ref.get("file", "N/A")
            print(f"   📍 {file_name}:{line}")

            if "context" in ref:
                context_lines = ref["context"].split("\n")
                for context_line in context_lines[:2]:  # Show first 2 context lines
                    print(f"      {context_line}")

    # Demo 4: Check for syntax errors
    print("\n4️⃣ Syntax Checking")
    print("-" * 30)

    result = await tool_manager.execute_tool(
        "GetDiagnosticsTool", file_path=test_file, language="python"
    )

    if result.success:
        data = result.data
        total = data.get("total_diagnostics", 0)
        errors = data.get("error_count", 0)
        warnings = data.get("warning_count", 0)

        if total == 0:
            print("✅ No syntax errors found!")
        else:
            print(f"⚠️  Found {total} issues ({errors} errors, {warnings} warnings)")

            diagnostics = data.get("diagnostics", [])
            for diag in diagnostics[:3]:  # Show first 3
                severity = diag.get("severity_name", "Unknown")
                message = diag.get("message", "No message")
                line = diag.get("line", 0) + 1
                print(f"   🚨 Line {line}: {severity} - {message}")

    print("\n" + "=" * 50)
    print("✨ Demo complete! Plato's embedded LSP tools provide:")
    print("   • Symbol detection and navigation")
    print("   • Basic reference finding")
    print("   • Syntax error detection")
    print("   • Code structure analysis")
    print("   • Fallback support when language servers unavailable")
    print("=" * 50)


async def main():
    """Main function."""
    try:
        await demo_lsp_capabilities()
        return 0
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
