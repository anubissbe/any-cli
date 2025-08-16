#!/usr/bin/env python3
"""
Test runner for Plato test suite.

This script provides a comprehensive test runner that:
1. Checks system prerequisites
2. Runs tests in logical order
3. Provides detailed reporting
4. Handles test failures gracefully
"""

import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import httpx
    import pytest
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )
    from rich.text import Text
except ImportError as e:
    print(f"Required dependency missing: {e}")
    print("Please install with: pip install httpx pytest rich")
    sys.exit(1)

console = Console()


class TestRunner:
    """Comprehensive test runner for Plato system."""

    def __init__(self):
        self.project_root = project_root
        self.test_results = {}
        self.prerequisites = {
            "serena_mcp": False,
            "plato_server": False,
            "python_deps": False,
        }

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        console.print("\n[bold blue]Checking Prerequisites...[/bold blue]")

        # Check Python dependencies
        try:
            import pytest
            import httpx
            import asyncio

            self.prerequisites["python_deps"] = True
            console.print("✅ Python dependencies available")
        except ImportError as e:
            console.print(f"❌ Missing Python dependency: {e}")
            self.prerequisites["python_deps"] = False

        # Check Serena MCP server
        try:
            response = httpx.get("http://localhost:8765/health", timeout=5.0)
            if response.status_code == 200:
                self.prerequisites["serena_mcp"] = True
                console.print("✅ Serena MCP server running on port 8765")
            else:
                console.print(
                    f"⚠️  Serena MCP server returned status {response.status_code}"
                )
        except Exception:
            console.print("❌ Serena MCP server not available on port 8765")
            console.print("   Start with: ./start_serena_mcp.sh start")

        # Check Plato server
        try:
            response = httpx.get("http://localhost:8080/health", timeout=5.0)
            if response.status_code == 200:
                self.prerequisites["plato_server"] = True
                console.print("✅ Plato server running on port 8080")
            else:
                console.print(f"⚠️  Plato server returned status {response.status_code}")
        except Exception:
            console.print("❌ Plato server not available on port 8080")
            console.print("   Start with: python -m plato.server.api")

        return all(self.prerequisites.values())

    def run_test_category(
        self, test_file: str, category: str, markers: str = ""
    ) -> Tuple[bool, Dict]:
        """Run a specific test category."""
        console.print(f"\n[bold green]Running {category} Tests[/bold green]")

        cmd = [
            "python",
            "-m",
            "pytest",
            f"tests/{test_file}",
            "-v",
            "--tb=short",
            "--disable-warnings",
            f"--junitxml=test_results_{category}.xml",
        ]

        if markers:
            cmd.extend(["-m", markers])

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                console.print(f"✅ {category} tests PASSED ({duration:.1f}s)")
                status = "PASSED"
            else:
                console.print(f"❌ {category} tests FAILED ({duration:.1f}s)")
                status = "FAILED"
                console.print(f"[red]STDOUT:[/red]\n{result.stdout}")
                console.print(f"[red]STDERR:[/red]\n{result.stderr}")

            return status == "PASSED", {
                "status": status,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            console.print(f"⏰ {category} tests TIMED OUT")
            return False, {
                "status": "TIMEOUT",
                "duration": 300,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "returncode": -1,
            }
        except Exception as e:
            console.print(f"💥 {category} tests ERROR: {e}")
            return False, {
                "status": "ERROR",
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
            }

    def run_unit_tests(self) -> bool:
        """Run unit tests."""
        return self.run_test_category("test_basic.py", "Unit", "unit")[0]

    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        success = True

        # AI Router integration tests
        passed, result = self.run_test_category(
            "test_ai_router_integration.py", "AI Router Integration", "integration"
        )
        self.test_results["ai_router"] = result
        success = success and passed

        # MCP Manager integration tests
        passed, result = self.run_test_category(
            "test_mcp_manager_integration.py", "MCP Manager Integration", "integration"
        )
        self.test_results["mcp_manager"] = result
        success = success and passed

        # Serena integration tests (if available)
        if self.prerequisites["serena_mcp"]:
            passed, result = self.run_test_category(
                "test_serena_integration.py", "Serena MCP Integration", "integration"
            )
            self.test_results["serena"] = result
            success = success and passed
        else:
            console.print("⏭️  Skipping Serena integration tests (server not available)")
            self.test_results["serena"] = {
                "status": "SKIPPED",
                "reason": "Server not available",
            }

        # API integration tests (if server available)
        if self.prerequisites["plato_server"]:
            passed, result = self.run_test_category(
                "test_api_integration.py", "API Integration", "integration"
            )
            self.test_results["api"] = result
            success = success and passed
        else:
            console.print("⏭️  Skipping API integration tests (server not available)")
            self.test_results["api"] = {
                "status": "SKIPPED",
                "reason": "Server not available",
            }

        # CLI integration tests
        passed, result = self.run_test_category(
            "test_cli_integration.py", "CLI Integration", "integration"
        )
        self.test_results["cli"] = result
        success = success and passed

        return success

    def run_end_to_end_tests(self) -> bool:
        """Run end-to-end tests."""
        if not self.prerequisites["serena_mcp"]:
            console.print("⏭️  Skipping E2E tests (Serena MCP not available)")
            self.test_results["e2e"] = {
                "status": "SKIPPED",
                "reason": "Serena not available",
            }
            return True

        passed, result = self.run_test_category(
            "test_end_to_end.py", "End-to-End", "integration and slow"
        )
        self.test_results["e2e"] = result
        return passed

    def generate_report(self):
        """Generate a comprehensive test report."""
        console.print("\n[bold blue]Test Report[/bold blue]")

        # Prerequisites table
        prereq_table = Table(title="Prerequisites")
        prereq_table.add_column("Component", style="cyan")
        prereq_table.add_column("Status", style="green")
        prereq_table.add_column("Notes", style="yellow")

        for name, status in self.prerequisites.items():
            status_text = "✅ Available" if status else "❌ Missing"
            notes = ""
            if name == "serena_mcp" and not status:
                notes = "Start with ./start_serena_mcp.sh start"
            elif name == "plato_server" and not status:
                notes = "Start with python -m plato.server.api"

            prereq_table.add_row(name.replace("_", " ").title(), status_text, notes)

        console.print(prereq_table)

        # Test results table
        if self.test_results:
            results_table = Table(title="Test Results")
            results_table.add_column("Test Category", style="cyan")
            results_table.add_column("Status", style="green")
            results_table.add_column("Duration", style="yellow")
            results_table.add_column("Notes", style="red")

            total_duration = 0
            passed_count = 0
            total_count = 0

            for category, result in self.test_results.items():
                status = result["status"]
                duration = result.get("duration", 0)
                total_duration += duration
                total_count += 1

                if status == "PASSED":
                    status_text = "✅ PASSED"
                    passed_count += 1
                elif status == "FAILED":
                    status_text = "❌ FAILED"
                elif status == "SKIPPED":
                    status_text = "⏭️ SKIPPED"
                elif status == "TIMEOUT":
                    status_text = "⏰ TIMEOUT"
                else:
                    status_text = "💥 ERROR"

                duration_text = f"{duration:.1f}s" if duration > 0 else "N/A"
                notes = result.get("reason", "")

                results_table.add_row(
                    category.replace("_", " ").title(),
                    status_text,
                    duration_text,
                    notes,
                )

            console.print(results_table)

            # Summary
            summary_panel = Panel(
                f"[bold]Summary:[/bold] {passed_count}/{total_count} test categories passed\n"
                f"[bold]Total Duration:[/bold] {total_duration:.1f} seconds\n"
                f"[bold]Success Rate:[/bold] {(passed_count/total_count*100):.1f}%",
                title="Test Summary",
                border_style="green" if passed_count == total_count else "red",
            )
            console.print(summary_panel)

    def run_all_tests(self, include_e2e: bool = True) -> bool:
        """Run all test categories."""
        console.print(
            Panel.fit(
                "[bold blue]Plato Test Suite[/bold blue]\n"
                "Comprehensive testing of AI orchestration system",
                border_style="blue",
            )
        )

        # Check prerequisites
        prereqs_ok = self.check_prerequisites()

        if not self.prerequisites["python_deps"]:
            console.print("[red]Cannot run tests without Python dependencies![/red]")
            return False

        # Run tests in order
        all_passed = True

        # Unit tests (always run)
        console.print("\n[bold cyan]Phase 1: Unit Tests[/bold cyan]")
        unit_passed = self.run_unit_tests()
        all_passed = all_passed and unit_passed

        # Integration tests
        console.print("\n[bold cyan]Phase 2: Integration Tests[/bold cyan]")
        integration_passed = self.run_integration_tests()
        all_passed = all_passed and integration_passed

        # End-to-end tests (if requested and possible)
        if include_e2e:
            console.print("\n[bold cyan]Phase 3: End-to-End Tests[/bold cyan]")
            e2e_passed = self.run_end_to_end_tests()
            all_passed = all_passed and e2e_passed

        # Generate report
        self.generate_report()

        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Plato test suite")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration-only", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--no-e2e", action="store_true", help="Skip end-to-end tests")
    parser.add_argument(
        "--check-prereqs", action="store_true", help="Only check prerequisites"
    )

    args = parser.parse_args()

    runner = TestRunner()

    if args.check_prereqs:
        runner.check_prerequisites()
        return

    success = False

    if args.unit_only:
        console.print("[bold]Running Unit Tests Only[/bold]")
        success = runner.run_unit_tests()
    elif args.integration_only:
        console.print("[bold]Running Integration Tests Only[/bold]")
        success = runner.run_integration_tests()
    else:
        console.print("[bold]Running Full Test Suite[/bold]")
        success = runner.run_all_tests(include_e2e=not args.no_e2e)

    if success:
        console.print("\n[bold green]🎉 All tests passed![/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold red]❌ Some tests failed![/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
