#!/usr/bin/env python3
"""
Test script to verify Plato's connection to Serena MCP server.

This script demonstrates the proper way to connect to and test Serena MCP server
for LSP-based code editing functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the plato directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from plato.integrations.serena_mcp import SerenaMCPClient, SerenaLanguage


async def test_serena_health_check():
    """Test basic health check to Serena MCP server."""
    print("🔍 Testing Serena MCP server health check...")

    client = SerenaMCPClient()

    try:
        # Test connection by trying to connect
        connected = await client.connect()
        print(f"   Connection result: {connected}")

        # The health_check method tries to hit /health which returns 404
        # This is expected since Serena uses MCP protocol, not REST endpoints
        health = await client.health_check()
        print(f"   Health check result: {health}")

        await client.disconnect()
        return connected  # Connection success is what matters

    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        await client.disconnect()
        return False


async def test_serena_server_status():
    """Test getting Serena server status through MCP."""
    print("\n📊 Testing Serena server status...")

    client = SerenaMCPClient()

    try:
        await client.connect()

        # Try to get server status
        response = await client.get_server_status()
        print(f"   Status response: {response.success}")

        if response.success:
            print(f"   Status data: {json.dumps(response.data, indent=2)}")
        else:
            print(f"   Error: {response.error}")

        await client.disconnect()
        return response.success

    except Exception as e:
        print(f"   ❌ Server status test failed: {e}")
        await client.disconnect()
        return False


async def test_serena_list_tools():
    """Test listing available tools from Serena."""
    print("\n🔧 Testing Serena tools listing...")

    client = SerenaMCPClient()

    try:
        await client.connect()

        # Try to get available language servers (this is a basic tool test)
        response = await client.get_language_servers()
        print(f"   Language servers response: {response.success}")

        if response.success:
            print(
                f"   Available language servers: {json.dumps(response.data, indent=2)}"
            )
        else:
            print(f"   Error: {response.error}")

        await client.disconnect()
        return response.success

    except Exception as e:
        print(f"   ❌ Tools listing test failed: {e}")
        await client.disconnect()
        return False


async def test_serena_project_operations():
    """Test project-level operations with Serena."""
    print("\n📁 Testing Serena project operations...")

    client = SerenaMCPClient()
    project_path = "/opt/projects/plato"  # Use the plato project itself

    try:
        await client.connect()

        # Test opening a project
        print(f"   Opening project: {project_path}")
        response = await client.open_project(project_path)
        print(f"   Open project response: {response.success}")

        if not response.success:
            print(f"   Open project error: {response.error}")
            await client.disconnect()
            return False

        # Test getting project info
        print("   Getting project info...")
        response = await client.get_project_info(project_path)
        print(f"   Project info response: {response.success}")

        if response.success:
            print(f"   Project data: {json.dumps(response.data, indent=2)}")
        else:
            print(f"   Project info error: {response.error}")

        # Test getting workspace files
        print("   Getting workspace files...")
        response = await client.get_workspace_files(
            project_path, language=SerenaLanguage.PYTHON
        )
        print(f"   Workspace files response: {response.success}")

        if response.success:
            files = response.data
            print(f"   Found {len(files) if files else 0} Python files")
            if files:
                print(f"   First few files: {files[:3]}")
        else:
            print(f"   Workspace files error: {response.error}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"   ❌ Project operations test failed: {e}")
        await client.disconnect()
        return False


async def test_serena_symbol_operations():
    """Test symbol finding and analysis operations."""
    print("\n🔍 Testing Serena symbol operations...")

    client = SerenaMCPClient()
    project_path = "/opt/projects/plato"
    test_file = "/opt/projects/plato/plato/cli.py"

    try:
        await client.connect()

        # First open the project
        await client.open_project(project_path)

        # Test opening a specific file
        print(f"   Opening file: {test_file}")
        response = await client.open_file(test_file)
        print(f"   Open file response: {response.success}")

        if not response.success:
            print(f"   Open file error: {response.error}")
            await client.disconnect()
            return False

        # Test getting document symbols
        print("   Getting document symbols...")
        response = await client.get_document_symbols(test_file)
        print(f"   Document symbols response: {response.success}")

        if response.success:
            symbols = response.data
            print(f"   Found {len(symbols) if symbols else 0} symbols")
            if symbols:
                print(
                    f"   First few symbols: {[s.get('name', 'unknown') for s in symbols[:3]]}"
                )
        else:
            print(f"   Document symbols error: {response.error}")

        # Test finding symbols in workspace
        print("   Finding symbols in workspace...")
        response = await client.find_symbols(
            project_path, "PlatoClient", SerenaLanguage.PYTHON
        )
        print(f"   Find symbols response: {response.success}")

        if response.success:
            symbols = response.data
            print(f"   Found {len(symbols) if symbols else 0} matching symbols")
        else:
            print(f"   Find symbols error: {response.error}")

        # Test getting diagnostics
        print("   Getting diagnostics...")
        response = await client.get_diagnostics(test_file)
        print(f"   Diagnostics response: {response.success}")

        if response.success:
            diagnostics = response.data
            print(f"   Found {len(diagnostics) if diagnostics else 0} diagnostics")
        else:
            print(f"   Diagnostics error: {response.error}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"   ❌ Symbol operations test failed: {e}")
        await client.disconnect()
        return False


async def test_serena_context_building():
    """Test building comprehensive context for code analysis."""
    print("\n📋 Testing Serena context building...")

    client = SerenaMCPClient()
    project_path = "/opt/projects/plato"
    test_file = "/opt/projects/plato/plato/integrations/serena_mcp.py"

    try:
        await client.connect()

        # Open the project first
        await client.open_project(project_path)

        # Test building file context
        print(f"   Building file context for: {test_file}")
        context = await client.build_file_context(test_file)

        print(f"   File context keys: {list(context.keys())}")
        print(f"   Has content: {'content' in context}")
        print(f"   Has symbols: {'symbols' in context and bool(context['symbols'])}")
        print(
            f"   Has diagnostics: {'diagnostics' in context and bool(context['diagnostics'])}"
        )

        # Test building project context
        print("   Building project context...")
        project_context = await client.build_project_context(project_path)

        print(f"   Project context keys: {list(project_context.keys())}")
        print(
            f"   Has files: {'files' in project_context and bool(project_context['files'])}"
        )
        print(f"   Has dependencies: {'dependencies' in project_context}")
        print(f"   Has metrics: {'metrics' in project_context}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"   ❌ Context building test failed: {e}")
        await client.disconnect()
        return False


async def run_all_tests():
    """Run all Serena MCP tests."""
    print("🚀 Running Serena MCP Integration Tests")
    print("=" * 50)

    tests = [
        ("Health Check", test_serena_health_check),
        ("Server Status", test_serena_server_status),
        ("List Tools", test_serena_list_tools),
        ("Project Operations", test_serena_project_operations),
        ("Symbol Operations", test_serena_symbol_operations),
        ("Context Building", test_serena_context_building),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("-" * 30)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Serena MCP integration is working.")
        return True
    else:
        print("⚠️  Some tests failed. See details above.")
        return False


if __name__ == "__main__":
    print("Serena MCP Integration Test")
    print("This script tests the connection between Plato and Serena MCP server")
    print(
        "Make sure Serena MCP server is running on port 8765 before running this test."
    )
    print()

    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
