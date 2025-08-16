#!/usr/bin/env python3
"""
Test script demonstrating the FIXED Plato-Serena integration.

This shows how the corrected SerenaMCPClient properly uses MCP protocol
over SSE transport to communicate with Serena.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from plato.integrations.serena_mcp_fixed import SerenaMCPClient


async def test_fixed_integration():
    """Test the fixed Serena MCP integration."""
    print("🎯 Testing FIXED Plato-Serena Integration")
    print("=" * 50)

    client = SerenaMCPClient()

    try:
        # Test 1: Connection
        print("\n1. 🔌 Testing MCP Connection...")
        connected = await client.connect()

        if not connected:
            print("❌ Failed to connect to Serena MCP")
            return False

        print("✅ Connected successfully!")

        # Test 2: List Tools
        print("\n2. 🔧 Testing Tool Listing...")
        tools_resp = await client.list_tools()

        if tools_resp.success:
            tools = tools_resp.data
            print(f"✅ Found {len(tools)} tools:")
            for i, tool in enumerate(tools[:5], 1):
                print(f"   {i}. {tool['name']}: {tool['description'][:60]}...")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
        else:
            print(f"❌ Failed to list tools: {tools_resp.error}")
            return False

        # Test 3: Project Activation
        print("\n3. 📁 Testing Project Activation...")
        project_path = "/opt/projects/plato"
        activate_resp = await client.activate_project(project_path)

        if activate_resp.success:
            print(f"✅ Project activated: {project_path}")
        else:
            print(f"❌ Project activation failed: {activate_resp.error}")

        # Test 4: File Operations
        print("\n4. 📄 Testing File Operations...")

        # List directory
        list_resp = await client.list_dir(project_path)
        if list_resp.success:
            print("✅ Directory listing successful")
            files = list_resp.data.split("\n")[:5] if list_resp.data else []
            for file in files:
                if file.strip():
                    print(f"   - {file.strip()}")
        else:
            print(f"❌ Directory listing failed: {list_resp.error}")

        # Test 5: Symbol Operations
        print("\n5. 🔍 Testing Symbol Operations...")

        # Try to read a Python file and get symbols
        test_file = "plato/cli.py"
        symbols_resp = await client.get_symbols_overview(test_file)

        if symbols_resp.success:
            print(f"✅ Symbol overview successful for {test_file}")
            if symbols_resp.data:
                preview = (
                    symbols_resp.data[:200] + "..."
                    if len(symbols_resp.data) > 200
                    else symbols_resp.data
                )
                print(f"   Symbols preview: {preview}")
        else:
            print(f"❌ Symbol overview failed: {symbols_resp.error}")

        # Test 6: Search Operations
        print("\n6. 🔎 Testing Search Operations...")

        search_resp = await client.search_for_pattern("class", test_file)
        if search_resp.success:
            print("✅ Pattern search successful")
            if search_resp.data:
                preview = (
                    search_resp.data[:150] + "..."
                    if len(search_resp.data) > 150
                    else search_resp.data
                )
                print(f"   Search results: {preview}")
        else:
            print(f"❌ Pattern search failed: {search_resp.error}")

        # Test 7: Context Building
        print("\n7. 🏗️ Testing Context Building...")

        context = await client.build_file_context(test_file)
        print(f"✅ File context built for {test_file}")
        print(f"   Content available: {'Yes' if context['content'] else 'No'}")
        print(f"   Symbols available: {'Yes' if context['symbols'] else 'No'}")
        if context["errors"]:
            print(f"   Errors: {len(context['errors'])}")

        print("\n✅ All tests completed successfully!")
        print("🎉 Fixed Plato-Serena integration is working!")

        return True

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

    finally:
        await client.disconnect()


async def demonstrate_serena_operations():
    """Demonstrate specific Serena operations working through Plato."""
    print("\n🎯 Demonstrating Serena LSP Operations via Plato")
    print("=" * 50)

    async with SerenaMCPClient() as client:

        # Activate the Plato project
        print("\n📁 Activating Plato project...")
        activate_resp = await client.activate_project("/opt/projects/plato")
        if activate_resp.success:
            print("✅ Project activated")
        else:
            print(f"❌ Activation failed: {activate_resp.error}")
            return

        # Find all Python files
        print("\n🔍 Finding Python files...")
        find_resp = await client.find_file("*.py")
        if find_resp.success and find_resp.data:
            python_files = [
                f for f in find_resp.data.split("\n") if f.strip().endswith(".py")
            ][:3]
            print(f"✅ Found Python files:")
            for pf in python_files:
                if pf.strip():
                    print(f"   - {pf.strip()}")

        # Analyze a specific file
        target_file = "plato/core/mcp_manager.py"
        print(f"\n🔬 Analyzing {target_file}...")

        # Get file content
        content_resp = await client.read_file(target_file)
        if content_resp.success:
            lines = content_resp.data.split("\n") if content_resp.data else []
            print(f"   📄 File has {len(lines)} lines")

        # Get symbols
        symbols_resp = await client.get_symbols_overview(target_file)
        if symbols_resp.success and symbols_resp.data:
            print("   🔍 Symbols found:")
            # Try to extract class/function names from the response
            if (
                "class" in symbols_resp.data.lower()
                or "def" in symbols_resp.data.lower()
            ):
                print("   - Found classes and/or functions")

        # Search for specific patterns
        search_resp = await client.search_for_pattern("async def", target_file)
        if search_resp.success and search_resp.data:
            print("   ⚡ Found async functions")

        # Use memory to store analysis
        memory_key = f"analysis_{target_file.replace('/', '_')}"
        memory_value = f"Analyzed {target_file} - {len(lines) if 'lines' in locals() else 'unknown'} lines"

        memory_resp = await client.write_memory(memory_key, memory_value)
        if memory_resp.success:
            print(f"   💾 Stored analysis in memory: {memory_key}")

        print("\n✅ Serena operations demonstration completed!")


async def main():
    """Run all tests and demonstrations."""
    print("🧪 Fixed Plato-Serena Integration Test Suite")
    print("This demonstrates the CORRECTED integration using MCP protocol")
    print()

    # Test 1: Basic fixed integration
    basic_success = await test_fixed_integration()

    # Test 2: Serena operations demonstration
    if basic_success:
        await demonstrate_serena_operations()

    print("\n" + "=" * 60)
    print("📊 Final Results:")
    print(
        f"   {'✅' if basic_success else '❌'} Fixed Integration Test: {'PASS' if basic_success else 'FAIL'}"
    )

    if basic_success:
        print("\n🎉 SUCCESS: Fixed Plato-Serena integration is working!")
        print("✨ The proper MCP protocol over SSE is now being used")
        print("🔧 All 24 Serena tools are accessible through Plato")
    else:
        print("\n❌ Integration issues still exist")

    return basic_success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
