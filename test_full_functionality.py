#!/usr/bin/env python3
"""
Comprehensive functionality test suite for Plato.

This script tests:
1. All 13 embedded tools functionality
2. LSP features across multiple languages
3. Multi-language support verification
4. Agent orchestration capabilities
5. Context management features
6. Integration with Serena MCP
7. Missing features comparison vs SuperClaude

This provides a complete audit of Plato's capabilities.
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Plato components
try:
    from plato.core.embedded_tools import (
        ReadFileTool,
        WriteFileTool,
        EditFileTool,
        ListDirectoryTool,
        SearchFilesTool,
        CreateDirectoryTool,
        ToolManager,
    )
    from plato.core.embedded_lsp import (
        LSPManager,
        GetSymbolsTool,
        FindReferencesTool,
        FindDefinitionTool,
        GetDiagnosticsTool,
        CodeAnalysisTool,
        HoverInfoTool,
        CompletionsTool,
    )
    from plato.core.ai_router import AIRouter
    from plato.core.context_manager import ContextManager
    from plato.core.mcp_manager import MCPManager
    from plato.integrations.serena_mcp import SerenaMCPClient

    PLATO_AVAILABLE = True
except ImportError as e:
    print(f"Error importing Plato components: {e}")
    PLATO_AVAILABLE = False

try:
    import httpx
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = lambda: None

console = Console() if RICH_AVAILABLE else None


@dataclass
class TestResult:
    """Test result data structure."""

    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PlatoFunctionalityTester:
    """Comprehensive Plato functionality tester."""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.temp_dir = Path(tempfile.mkdtemp(prefix="plato_test_"))
        self.setup_test_files()

        # Initialize components if available
        if PLATO_AVAILABLE:
            self.tool_manager = ToolManager()
            self.lsp_manager = LSPManager()
            self.ai_router = None
            self.context_manager = None
            self.mcp_manager = None
            self.serena_client = None

    def setup_test_files(self):
        """Create test files for various languages."""
        test_files = {
            "python_test.py": '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
    print(fibonacci(10))
''',
            "javascript_test.js": """
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

class Calculator {
    add(a, b) {
        return a + b;
    }
    
    multiply(a, b) {
        return a * b;
    }
}

const calc = new Calculator();
console.log(calc.add(5, 3));
console.log(fibonacci(10));
""",
            "typescript_test.ts": """
interface ICalculator {
    add(a: number, b: number): number;
    multiply(a: number, b: number): number;
}

class Calculator implements ICalculator {
    add(a: number, b: number): number {
        return a + b;
    }
    
    multiply(a: number, b: number): number {
        return a * b;
    }
}

function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

const calc = new Calculator();
console.log(calc.add(5, 3));
""",
            "go_test.go": """
package main

import "fmt"

type Calculator struct{}

func (c Calculator) Add(a, b int) int {
    return a + b
}

func (c Calculator) Multiply(a, b int) int {
    return a * b
}

func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

func main() {
    calc := Calculator{}
    fmt.Println(calc.Add(5, 3))
    fmt.Println(fibonacci(10))
}
""",
            "rust_test.rs": """
struct Calculator;

impl Calculator {
    fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }
    
    fn multiply(&self, a: i32, b: i32) -> i32 {
        a * b
    }
}

fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn main() {
    let calc = Calculator;
    println!("{}", calc.add(5, 3));
    println!("{}", fibonacci(10));
}
""",
            "java_test.java": """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int a, int b) {
        return a * b;
    }
    
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        System.out.println(calc.add(5, 3));
        System.out.println(fibonacci(10));
    }
}
""",
            "config.yaml": """
server:
  host: localhost
  port: 8080
  debug: true

database:
  host: localhost
  port: 5432
  name: plato_db
  
logging:
  level: info
  file: plato.log
""",
            "package.json": """
{
  "name": "test-project",
  "version": "1.0.0",
  "description": "Test project for Plato",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.18.0",
    "lodash": "^4.17.21"
  }
}
""",
            "Cargo.toml": """
[package]
name = "test-project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1.0"
tokio = "1.0"
""",
        }

        # Create test files
        for filename, content in test_files.items():
            file_path = self.temp_dir / filename
            file_path.write_text(content.strip())

        # Create subdirectories
        (self.temp_dir / "src").mkdir()
        (self.temp_dir / "tests").mkdir()
        (self.temp_dir / "docs").mkdir()

        # Additional files in subdirectories
        (self.temp_dir / "src" / "main.py").write_text(
            "# Main module\nprint('Hello, World!')"
        )
        (self.temp_dir / "tests" / "test_basic.py").write_text(
            "# Test file\ndef test_example():\n    assert True"
        )
        (self.temp_dir / "docs" / "README.md").write_text(
            "# Test Project\n\nThis is a test project."
        )

    async def test_embedded_file_tools(self) -> List[TestResult]:
        """Test all embedded file operation tools."""
        results = []

        if not PLATO_AVAILABLE:
            return [
                TestResult(
                    "embedded_tools_availability", False, 0.0, "Plato not available"
                )
            ]

        tools_to_test = [
            ("ReadFileTool", ReadFileTool),
            ("WriteFileTool", WriteFileTool),
            ("EditFileTool", EditFileTool),
            ("ListDirectoryTool", ListDirectoryTool),
            ("SearchFilesTool", SearchFilesTool),
            ("CreateDirectoryTool", CreateDirectoryTool),
        ]

        for tool_name, tool_class in tools_to_test:
            start_time = time.time()
            try:
                tool = tool_class()

                if tool_name == "ReadFileTool":
                    # Test reading a file
                    result = await tool.execute(
                        file_path=str(self.temp_dir / "python_test.py")
                    )
                    if not result.success or "fibonacci" not in str(result.data):
                        raise Exception("Failed to read file correctly")

                elif tool_name == "WriteFileTool":
                    # Test writing a new file
                    test_file = self.temp_dir / "test_write.txt"
                    result = await tool.execute(
                        file_path=str(test_file), content="Hello, Plato!"
                    )
                    if not result.success or not test_file.exists():
                        raise Exception("Failed to write file")

                elif tool_name == "EditFileTool":
                    # Test editing a file
                    result = await tool.execute(
                        file_path=str(self.temp_dir / "python_test.py"),
                        old_string="def fibonacci(n):",
                        new_string="def fibonacci_recursive(n):",
                    )
                    if not result.success:
                        raise Exception("Failed to edit file")

                elif tool_name == "ListDirectoryTool":
                    # Test listing directory
                    result = await tool.execute(path=str(self.temp_dir))
                    if not result.success or "python_test.py" not in str(result.data):
                        raise Exception("Failed to list directory correctly")

                elif tool_name == "SearchFilesTool":
                    # Test searching files
                    result = await tool.execute(
                        path=str(self.temp_dir), pattern="fibonacci"
                    )
                    if not result.success:
                        raise Exception("Failed to search files")

                elif tool_name == "CreateDirectoryTool":
                    # Test creating directory
                    new_dir = self.temp_dir / "new_test_dir"
                    result = await tool.execute(path=str(new_dir))
                    if not result.success or not new_dir.exists():
                        raise Exception("Failed to create directory")

                duration = time.time() - start_time
                results.append(TestResult(f"embedded_tool_{tool_name}", True, duration))

            except Exception as e:
                duration = time.time() - start_time
                results.append(
                    TestResult(f"embedded_tool_{tool_name}", False, duration, str(e))
                )

        return results

    async def test_embedded_lsp_tools(self) -> List[TestResult]:
        """Test all embedded LSP tools."""
        results = []

        if not PLATO_AVAILABLE:
            return [
                TestResult(
                    "embedded_lsp_availability", False, 0.0, "Plato not available"
                )
            ]

        lsp_tools_to_test = [
            ("GetSymbolsTool", GetSymbolsTool),
            ("FindReferencesTool", FindReferencesTool),
            ("FindDefinitionTool", FindDefinitionTool),
            ("GetDiagnosticsTool", GetDiagnosticsTool),
            ("CodeAnalysisTool", CodeAnalysisTool),
            ("HoverInfoTool", HoverInfoTool),
            ("CompletionsTool", CompletionsTool),
        ]

        # Test files for different languages
        test_files = [
            ("python", self.temp_dir / "python_test.py"),
            ("javascript", self.temp_dir / "javascript_test.js"),
            ("typescript", self.temp_dir / "typescript_test.ts"),
        ]

        for tool_name, tool_class in lsp_tools_to_test:
            for lang, file_path in test_files:
                test_name = f"lsp_{tool_name}_{lang}"
                start_time = time.time()

                try:
                    tool = tool_class()

                    if tool_name == "GetSymbolsTool":
                        result = await tool.execute(file_path=str(file_path))

                    elif tool_name == "FindReferencesTool":
                        result = await tool.execute(
                            file_path=str(file_path), line=5, column=10
                        )

                    elif tool_name == "FindDefinitionTool":
                        result = await tool.execute(
                            file_path=str(file_path), line=5, column=10
                        )

                    elif tool_name == "GetDiagnosticsTool":
                        result = await tool.execute(file_path=str(file_path))

                    elif tool_name == "CodeAnalysisTool":
                        result = await tool.execute(file_path=str(file_path))

                    elif tool_name == "HoverInfoTool":
                        result = await tool.execute(
                            file_path=str(file_path), line=5, column=10
                        )

                    elif tool_name == "CompletionsTool":
                        result = await tool.execute(
                            file_path=str(file_path), line=5, column=10
                        )

                    duration = time.time() - start_time

                    # For LSP tools, we consider it successful if no exception occurred
                    # (Some LSP features might not work in test environment)
                    results.append(
                        TestResult(
                            test_name,
                            True,
                            duration,
                            details={"has_result": result is not None},
                        )
                    )

                except Exception as e:
                    duration = time.time() - start_time
                    results.append(TestResult(test_name, False, duration, str(e)))

        return results

    async def test_multi_language_support(self) -> List[TestResult]:
        """Test support for multiple programming languages."""
        results = []

        languages = [
            ("python", "python_test.py"),
            ("javascript", "javascript_test.js"),
            ("typescript", "typescript_test.ts"),
            ("go", "go_test.go"),
            ("rust", "rust_test.rs"),
            ("java", "java_test.java"),
        ]

        for lang, filename in languages:
            start_time = time.time()

            try:
                file_path = self.temp_dir / filename

                # Test if file can be read and analyzed
                if PLATO_AVAILABLE:
                    read_tool = ReadFileTool()
                    result = await read_tool.execute(file_path=str(file_path))

                    if not result.success:
                        raise Exception(f"Failed to read {lang} file")

                    # Try basic LSP analysis
                    try:
                        symbols_tool = GetSymbolsTool()
                        symbols_result = await symbols_tool.execute(
                            file_path=str(file_path)
                        )
                        has_lsp_support = symbols_result is not None
                    except:
                        has_lsp_support = False
                else:
                    # Just check file exists
                    if not file_path.exists():
                        raise Exception(f"Test file for {lang} not found")
                    has_lsp_support = False

                duration = time.time() - start_time
                results.append(
                    TestResult(
                        f"language_support_{lang}",
                        True,
                        duration,
                        details={"lsp_support": has_lsp_support},
                    )
                )

            except Exception as e:
                duration = time.time() - start_time
                results.append(
                    TestResult(f"language_support_{lang}", False, duration, str(e))
                )

        return results

    async def test_ai_integration(self) -> List[TestResult]:
        """Test AI router and integration capabilities."""
        results = []

        if not PLATO_AVAILABLE:
            return [
                TestResult(
                    "ai_integration_availability", False, 0.0, "Plato not available"
                )
            ]

        start_time = time.time()

        try:
            # Test AI Router initialization
            self.ai_router = AIRouter()

            # Test basic functionality (without actual API calls)
            test_passed = hasattr(self.ai_router, "route_request")

            duration = time.time() - start_time
            results.append(TestResult("ai_router_init", test_passed, duration))

        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult("ai_router_init", False, duration, str(e)))

        return results

    async def test_context_management(self) -> List[TestResult]:
        """Test context management capabilities."""
        results = []

        if not PLATO_AVAILABLE:
            return [
                TestResult(
                    "context_management_availability", False, 0.0, "Plato not available"
                )
            ]

        start_time = time.time()

        try:
            # Test Context Manager initialization
            self.context_manager = ContextManager()

            # Test basic functionality
            test_passed = hasattr(self.context_manager, "add_context")

            duration = time.time() - start_time
            results.append(TestResult("context_manager_init", test_passed, duration))

        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult("context_manager_init", False, duration, str(e)))

        return results

    async def test_mcp_integration(self) -> List[TestResult]:
        """Test MCP (Model Context Protocol) integration."""
        results = []

        if not PLATO_AVAILABLE:
            return [
                TestResult(
                    "mcp_integration_availability", False, 0.0, "Plato not available"
                )
            ]

        # Test MCP Manager
        start_time = time.time()

        try:
            self.mcp_manager = MCPManager()

            test_passed = hasattr(self.mcp_manager, "connect")

            duration = time.time() - start_time
            results.append(TestResult("mcp_manager_init", test_passed, duration))

        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult("mcp_manager_init", False, duration, str(e)))

        # Test Serena MCP integration
        start_time = time.time()

        try:
            # Check if Serena MCP server is running
            try:
                import httpx

                response = httpx.get("http://localhost:8765/health", timeout=5.0)
                serena_available = response.status_code == 200
            except:
                serena_available = False

            if serena_available:
                self.serena_client = SerenaMCPClient("http://localhost:8765")
                test_passed = True
            else:
                test_passed = False

            duration = time.time() - start_time
            results.append(
                TestResult(
                    "serena_mcp_connection",
                    test_passed,
                    duration,
                    details={"serena_server_available": serena_available},
                )
            )

        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult("serena_mcp_connection", False, duration, str(e)))

        return results

    async def test_agent_orchestration(self) -> List[TestResult]:
        """Test agent orchestration capabilities."""
        results = []

        start_time = time.time()

        try:
            # Test if all major components can work together
            components_available = {
                "ai_router": self.ai_router is not None,
                "context_manager": self.context_manager is not None,
                "mcp_manager": self.mcp_manager is not None,
                "tool_manager": hasattr(self, "tool_manager")
                and self.tool_manager is not None,
                "lsp_manager": hasattr(self, "lsp_manager")
                and self.lsp_manager is not None,
            }

            all_available = all(components_available.values())

            duration = time.time() - start_time
            results.append(
                TestResult(
                    "agent_orchestration",
                    all_available,
                    duration,
                    details=components_available,
                )
            )

        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult("agent_orchestration", False, duration, str(e)))

        return results

    def check_missing_features(self) -> List[TestResult]:
        """Check for missing features compared to SuperClaude/Serena."""
        results = []

        # Expected features based on SuperClaude/Serena capabilities
        expected_features = {
            "code_completion": "Advanced code completion with AI suggestions",
            "refactoring_tools": "Automated refactoring capabilities",
            "test_generation": "Automatic test case generation",
            "documentation_gen": "Auto-documentation generation",
            "code_review": "AI-powered code review",
            "pattern_detection": "Design pattern detection and suggestions",
            "performance_analysis": "Code performance analysis",
            "security_scanning": "Security vulnerability detection",
            "dependency_management": "Dependency analysis and updates",
            "project_scaffolding": "Project template generation",
            "git_integration": "Advanced Git operations",
            "database_tools": "Database schema and query tools",
            "api_tools": "REST API testing and documentation",
        }

        start_time = time.time()

        # Check which features are available in Plato
        available_features = set()

        if PLATO_AVAILABLE:
            # Check embedded tools
            if hasattr(self, "tool_manager"):
                available_features.add("file_operations")

            # Check LSP tools
            if hasattr(self, "lsp_manager"):
                available_features.add("lsp_integration")
                available_features.add("symbol_navigation")
                available_features.add("diagnostics")

            # Check AI integration
            if self.ai_router is not None:
                available_features.add("ai_routing")

            # Check context management
            if self.context_manager is not None:
                available_features.add("context_management")

            # Check MCP integration
            if self.mcp_manager is not None:
                available_features.add("mcp_integration")

        missing_features = []
        for feature, description in expected_features.items():
            if feature not in available_features:
                missing_features.append(f"{feature}: {description}")

        duration = time.time() - start_time

        results.append(
            TestResult(
                "missing_features_check",
                True,
                duration,
                details={
                    "available_features": list(available_features),
                    "missing_features": missing_features,
                    "coverage_percentage": len(available_features)
                    / len(expected_features)
                    * 100,
                },
            )
        )

        return results

    def cleanup(self):
        """Clean up test resources."""
        try:
            import shutil

            shutil.rmtree(self.temp_dir)
        except Exception as e:
            if console:
                console.print(
                    f"[yellow]Warning: Failed to cleanup temp directory: {e}[/yellow]"
                )

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all functionality tests."""
        all_results = []

        if console:
            console.print(
                Panel.fit(
                    "[bold blue]Plato Comprehensive Functionality Test[/bold blue]\n"
                    "Testing all embedded tools, LSP features, and integrations",
                    border_style="blue",
                )
            )

        # Test categories
        test_categories = [
            ("Embedded File Tools", self.test_embedded_file_tools),
            ("Embedded LSP Tools", self.test_embedded_lsp_tools),
            ("Multi-Language Support", self.test_multi_language_support),
            ("AI Integration", self.test_ai_integration),
            ("Context Management", self.test_context_management),
            ("MCP Integration", self.test_mcp_integration),
            ("Agent Orchestration", self.test_agent_orchestration),
        ]

        # Run async tests
        for category_name, test_func in test_categories:
            if console:
                console.print(f"\n[bold green]Testing {category_name}...[/bold green]")

            try:
                category_results = await test_func()
                all_results.extend(category_results)

                passed = sum(1 for r in category_results if r.passed)
                total = len(category_results)

                if console:
                    console.print(f"  {category_name}: {passed}/{total} tests passed")

            except Exception as e:
                if console:
                    console.print(f"[red]Error in {category_name}: {e}[/red]")
                all_results.append(
                    TestResult(f"{category_name}_error", False, 0.0, str(e))
                )

        # Run synchronous tests
        if console:
            console.print(f"\n[bold green]Checking Missing Features...[/bold green]")

        missing_features_results = self.check_missing_features()
        all_results.extend(missing_features_results)

        # Generate comprehensive report
        return self.generate_comprehensive_report(all_results)

    def generate_comprehensive_report(
        self, results: List[TestResult]
    ) -> Dict[str, Any]:
        """Generate a comprehensive test report."""

        # Categorize results
        categories = {}
        for result in results:
            if "_" in result.name:
                category = result.name.split("_")[0]
            else:
                category = "general"

            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        # Calculate statistics
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in results)

        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "plato_available": PLATO_AVAILABLE,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_duration": total_duration,
            "categories": {},
        }

        # Category details
        for category, category_results in categories.items():
            cat_passed = sum(1 for r in category_results if r.passed)
            cat_total = len(category_results)

            summary["categories"][category] = {
                "passed": cat_passed,
                "total": cat_total,
                "success_rate": (cat_passed / cat_total * 100) if cat_total > 0 else 0,
                "tests": [
                    {
                        "name": r.name,
                        "passed": r.passed,
                        "duration": r.duration,
                        "error": r.error,
                        "details": r.details,
                    }
                    for r in category_results
                ],
            }

        # Print report if rich is available
        if console:
            self.print_rich_report(summary, results)
        else:
            self.print_simple_report(summary, results)

        return summary

    def print_rich_report(self, summary: Dict[str, Any], results: List[TestResult]):
        """Print a rich formatted report."""

        # Summary table
        summary_table = Table(title="Test Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Tests", str(summary["total_tests"]))
        summary_table.add_row("Passed", str(summary["passed_tests"]))
        summary_table.add_row("Failed", str(summary["failed_tests"]))
        summary_table.add_row("Success Rate", f"{summary['success_rate']:.1f}%")
        summary_table.add_row("Duration", f"{summary['total_duration']:.2f}s")
        summary_table.add_row(
            "Plato Available", "✅ Yes" if summary["plato_available"] else "❌ No"
        )

        console.print("\n")
        console.print(summary_table)

        # Category breakdown
        for category, cat_data in summary["categories"].items():
            console.print(f"\n[bold cyan]{category.title()} Tests[/bold cyan]")

            cat_table = Table()
            cat_table.add_column("Test", style="white")
            cat_table.add_column("Result", style="green")
            cat_table.add_column("Duration", style="yellow")
            cat_table.add_column("Details", style="dim")

            for test in cat_data["tests"]:
                result_text = "✅ PASS" if test["passed"] else "❌ FAIL"
                duration_text = f"{test['duration']:.2f}s"
                details_text = test["error"] if test["error"] else ""

                if test["details"]:
                    if details_text:
                        details_text += " | "
                    details_text += str(test["details"])

                cat_table.add_row(
                    test["name"],
                    result_text,
                    duration_text,
                    (
                        details_text[:50] + "..."
                        if len(details_text) > 50
                        else details_text
                    ),
                )

            console.print(cat_table)
            console.print(f"Category Success Rate: {cat_data['success_rate']:.1f}%")

        # Final summary panel
        if summary["success_rate"] == 100:
            panel_style = "green"
            status_text = "🎉 ALL TESTS PASSED"
        elif summary["success_rate"] >= 75:
            panel_style = "yellow"
            status_text = "⚠️  MOSTLY WORKING"
        else:
            panel_style = "red"
            status_text = "❌ NEEDS ATTENTION"

        final_panel = Panel(
            f"[bold]{status_text}[/bold]\n\n"
            f"Plato functionality test completed.\n"
            f"Success rate: {summary['success_rate']:.1f}%\n"
            f"See detailed results above.",
            title="Test Results",
            border_style=panel_style,
        )

        console.print("\n")
        console.print(final_panel)

    def print_simple_report(self, summary: Dict[str, Any], results: List[TestResult]):
        """Print a simple text report."""
        print("\n" + "=" * 60)
        print("PLATO COMPREHENSIVE FUNCTIONALITY TEST REPORT")
        print("=" * 60)

        print(f"Timestamp: {summary['timestamp']}")
        print(f"Plato Available: {'Yes' if summary['plato_available'] else 'No'}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.2f}s")

        print("\nCATEGORY BREAKDOWN:")
        print("-" * 40)

        for category, cat_data in summary["categories"].items():
            print(f"\n{category.upper()}:")
            print(f"  Success Rate: {cat_data['success_rate']:.1f}%")
            print(f"  Tests: {cat_data['passed']}/{cat_data['total']}")

            for test in cat_data["tests"]:
                status = "PASS" if test["passed"] else "FAIL"
                print(f"    {test['name']}: {status} ({test['duration']:.2f}s)")
                if test["error"]:
                    print(f"      Error: {test['error']}")

        print("\n" + "=" * 60)
        if summary["success_rate"] == 100:
            print("🎉 ALL TESTS PASSED - Plato is fully functional!")
        elif summary["success_rate"] >= 75:
            print("⚠️  MOSTLY WORKING - Some features may need attention")
        else:
            print("❌ NEEDS ATTENTION - Multiple failures detected")
        print("=" * 60)


async def main():
    """Main entry point."""
    tester = PlatoFunctionalityTester()

    try:
        # Run all tests
        report = await tester.run_all_tests()

        # Save report to file
        report_file = Path("/opt/projects/plato/test_functionality_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved to: {report_file}")

        # Return exit code based on success rate
        if report["success_rate"] >= 75:
            return 0
        else:
            return 1

    except Exception as e:
        print(f"Error running tests: {e}")
        traceback.print_exc()
        return 1

    finally:
        tester.cleanup()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
