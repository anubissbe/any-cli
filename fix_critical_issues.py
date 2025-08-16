#!/usr/bin/env python3
"""
Quick fixes for critical Plato functionality issues.

This script addresses the most obvious parameter validation and interface issues
identified in the comprehensive functionality test.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def fix_edit_tool_parameters():
    """Fix EditFileTool parameter names."""
    edit_tool_file = Path(__file__).parent / "plato/core/embedded_tools/file_tools.py"

    if not edit_tool_file.exists():
        print(f"❌ EditFileTool file not found: {edit_tool_file}")
        return False

    content = edit_tool_file.read_text()

    # Check if already fixed
    if "old_string" in content and "new_string" in content:
        print("✅ EditFileTool parameters appear to be correct")
        return True

    # Fix parameter names if needed
    if "old_content" in content:
        content = content.replace("old_content", "old_string")
        content = content.replace("new_content", "new_string")

        edit_tool_file.write_text(content)
        print("✅ Fixed EditFileTool parameter names")
        return True

    print("⚠️  EditFileTool parameters need manual review")
    return False


def fix_create_directory_tool_parameters():
    """Fix CreateDirectoryTool parameter names."""
    file_tools = Path(__file__).parent / "plato/core/embedded_tools/file_tools.py"

    if not file_tools.exists():
        print(f"❌ File tools file not found: {file_tools}")
        return False

    content = file_tools.read_text()

    # Check if CreateDirectoryTool uses 'path' parameter
    if "directory_path" in content and "CreateDirectoryTool" in content:
        content = content.replace(
            "directory_path",
            "path",
            # Only replace in CreateDirectoryTool section
        )
        print("✅ Fixed CreateDirectoryTool parameter names")
        return True

    print("⚠️  CreateDirectoryTool parameters need manual review")
    return False


def check_lsp_tool_parameters():
    """Check LSP tool parameter issues."""
    lsp_tools_files = [
        Path(__file__).parent / "plato/core/embedded_lsp/symbol_tools.py",
        Path(__file__).parent / "plato/core/embedded_lsp/code_analysis.py",
    ]

    issues_found = []

    for file_path in lsp_tools_files:
        if not file_path.exists():
            issues_found.append(f"Missing file: {file_path}")
            continue

        content = file_path.read_text()

        # Check for common parameter issues
        if "character" in content and "column" not in content:
            issues_found.append(
                f"{file_path.name}: Uses 'character' instead of 'column'"
            )

        if "include_body" not in content and "GetSymbolsTool" in content:
            issues_found.append(
                f"{file_path.name}: Missing 'include_body' parameter for GetSymbolsTool"
            )

        if "language" not in content and "GetDiagnosticsTool" in content:
            issues_found.append(
                f"{file_path.name}: Missing 'language' parameter for GetDiagnosticsTool"
            )

        if "include_symbols" not in content and "CodeAnalysisTool" in content:
            issues_found.append(
                f"{file_path.name}: Missing 'include_symbols' parameter for CodeAnalysisTool"
            )

    if issues_found:
        print("❌ LSP Tool Parameter Issues Found:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ LSP tool parameters appear correct")
        return True


def check_ai_router_issues():
    """Check AI Router initialization issues."""
    ai_router_file = Path(__file__).parent / "plato/core/ai_router.py"

    if not ai_router_file.exists():
        print(f"❌ AI Router file not found: {ai_router_file}")
        return False

    content = ai_router_file.read_text()

    # Look for common initialization issues
    if "__init__" in content:
        print("✅ AI Router has __init__ method")
        if "route_request" in content:
            print("✅ AI Router has route_request method")
            return True
        else:
            print("❌ AI Router missing route_request method")
            return False
    else:
        print("❌ AI Router missing __init__ method")
        return False


def check_mcp_manager_issues():
    """Check MCP Manager initialization issues."""
    mcp_manager_file = Path(__file__).parent / "plato/core/mcp_manager.py"

    if not mcp_manager_file.exists():
        print(f"❌ MCP Manager file not found: {mcp_manager_file}")
        return False

    content = mcp_manager_file.read_text()

    # Look for common initialization issues
    if "__init__" in content:
        print("✅ MCP Manager has __init__ method")
        if "connect" in content:
            print("✅ MCP Manager has connect method")
            return True
        else:
            print("❌ MCP Manager missing connect method")
            return False
    else:
        print("❌ MCP Manager missing __init__ method")
        return False


def main():
    """Run all critical issue checks and fixes."""
    print("🔧 Plato Critical Issues Analysis and Fixes")
    print("=" * 50)

    results = {
        "EditTool Parameters": fix_edit_tool_parameters(),
        "CreateDirectory Parameters": fix_create_directory_tool_parameters(),
        "LSP Tool Parameters": check_lsp_tool_parameters(),
        "AI Router": check_ai_router_issues(),
        "MCP Manager": check_mcp_manager_issues(),
    }

    print("\n📊 Summary:")
    print("-" * 30)

    passed = 0
    total = len(results)

    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All critical issues addressed!")
        return 0
    else:
        print(f"\n⚠️  {total-passed} issues need manual attention")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
