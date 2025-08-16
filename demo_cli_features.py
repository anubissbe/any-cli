#!/usr/bin/env python3
"""
Comprehensive CLI demonstration for Plato system.
Shows all major CLI capabilities and features.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# Setup logging for demo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PlatoCLIDemo:
    """Demonstrate Plato CLI capabilities."""

    def __init__(self):
        self.project_root = Path("/opt/projects/plato")
        self.venv_python = self.project_root / "venv/bin/python"
        self.plato_cli = [str(self.venv_python), "-m", "plato.cli"]
        self.demo_results = []

    def run_command(self, cmd_args, description, timeout=30):
        """Run a CLI command and capture results."""
        full_cmd = self.plato_cli + cmd_args

        logger.info(f"🔧 {description}")
        logger.info(f"   Command: {' '.join(cmd_args)}")

        try:
            start_time = time.time()
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )

            duration = time.time() - start_time

            demo_result = {
                "description": description,
                "command": " ".join(cmd_args),
                "exit_code": result.returncode,
                "duration": round(duration, 2),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

            if demo_result["success"]:
                logger.info(f"   ✅ Success ({duration:.2f}s)")
                if result.stdout:
                    # Show first few lines of output
                    lines = result.stdout.strip().split("\n")
                    for line in lines[:3]:
                        logger.info(f"   → {line}")
                    if len(lines) > 3:
                        logger.info(f"   → ... ({len(lines)-3} more lines)")
            else:
                logger.error(f"   ❌ Failed ({duration:.2f}s)")
                if result.stderr:
                    logger.error(f"   Error: {result.stderr.strip()}")

            self.demo_results.append(demo_result)
            return demo_result

        except subprocess.TimeoutExpired:
            logger.error(f"   ⏱️ Timeout after {timeout}s")
            demo_result = {
                "description": description,
                "command": " ".join(cmd_args),
                "exit_code": -1,
                "duration": timeout,
                "stdout": "",
                "stderr": "Command timed out",
                "success": False,
            }
            self.demo_results.append(demo_result)
            return demo_result

        except Exception as e:
            logger.error(f"   💥 Exception: {e}")
            demo_result = {
                "description": description,
                "command": " ".join(cmd_args),
                "exit_code": -1,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "success": False,
            }
            self.demo_results.append(demo_result)
            return demo_result

    def demo_basic_commands(self):
        """Demonstrate basic CLI commands."""
        logger.info("📋 PHASE 1: Basic Commands")

        # Help command
        self.run_command(["--help"], "Show main help")

        # List available commands
        self.run_command(["chat", "--help"], "Show chat command help")

        # Health check
        self.run_command(["health"], "Check server health")

    def demo_ai_chat(self):
        """Demonstrate AI chat functionality."""
        logger.info("🤖 PHASE 2: AI Chat Features")

        # Simple chat
        self.run_command(
            [
                "chat",
                "Hello! Please respond with 'CLI test successful' and nothing else.",
            ],
            "Simple AI chat test",
        )

        # Chat with specific provider
        self.run_command(
            ["chat", "--provider", "openai", "What is 2+2?"],
            "Chat with OpenAI provider",
        )

        # Chat with token limit
        self.run_command(
            ["chat", "--max-tokens", "50", "Explain Python in one sentence."],
            "Chat with token limit",
        )

    def demo_project_operations(self):
        """Demonstrate project management."""
        logger.info("📁 PHASE 3: Project Operations")

        # Analyze current project
        self.run_command(["analyze", str(self.project_root)], "Analyze current project")

        # Analyze with specific operation
        self.run_command(
            ["analyze", str(self.project_root), "--operation", "build_context"],
            "Build project context",
        )

        # Analyze with language filter
        self.run_command(
            ["analyze", str(self.project_root), "--language", "python"],
            "Analyze Python files",
        )

    def demo_tool_operations(self):
        """Demonstrate tool operations."""
        logger.info("🔧 PHASE 4: Tool Operations")

        # List available tools
        self.run_command(["tools"], "List available tools")

        # Call a specific tool
        self.run_command(
            ["call-tool", "list_dir", "--arguments", '{"path": "."}'],
            "Call list_dir tool",
        )

        # Call read_file tool
        self.run_command(
            ["call-tool", "read_file", "--arguments", '{"path": "plato/__init__.py"}'],
            "Call read_file tool",
        )

    def demo_interactive_features(self):
        """Demonstrate interactive features."""
        logger.info("💬 PHASE 5: Interactive Features")

        # Start interactive mode with short timeout for demo
        self.run_command(
            ["interactive"], "Test interactive mode (will timeout)", timeout=5
        )

    def demo_advanced_tool_calls(self):
        """Demonstrate advanced tool calls."""
        logger.info("⚡ PHASE 6: Advanced Tool Calls")

        # Search for patterns
        self.run_command(
            ["call-tool", "search_for_pattern", "--arguments", '{"pattern": "class"}'],
            "Search for class patterns",
        )

        # Get symbols overview
        self.run_command(
            [
                "call-tool",
                "get_symbols_overview",
                "--arguments",
                '{"relative_path": "plato/__init__.py"}',
            ],
            "Get symbols overview",
        )

        # Find files
        self.run_command(
            ["call-tool", "find_file", "--arguments", '{"pattern": "*.py"}'],
            "Find Python files",
        )

    def demo_memory_operations(self):
        """Demonstrate memory operations via tools."""
        logger.info("💾 PHASE 7: Memory Operations")

        # Write to memory
        self.run_command(
            [
                "call-tool",
                "write_memory",
                "--arguments",
                '{"key": "demo_key", "value": "demo_value"}',
            ],
            "Write to memory",
        )

        # Read from memory
        self.run_command(
            ["call-tool", "read_memory", "--arguments", '{"key": "demo_key"}'],
            "Read from memory",
        )

        # List memories
        self.run_command(
            ["call-tool", "list_memories", "--arguments", "{}"], "List all memories"
        )

        # Delete memory
        self.run_command(
            ["call-tool", "delete_memory", "--arguments", '{"key": "demo_key"}'],
            "Delete memory",
        )

    def generate_report(self):
        """Generate demonstration report."""
        logger.info("📊 Generating CLI Demo Report")

        total_commands = len(self.demo_results)
        successful_commands = sum(1 for r in self.demo_results if r["success"])

        report = {
            "cli_demo_report": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_commands": total_commands,
                "successful_commands": successful_commands,
                "success_rate": (
                    round(successful_commands / total_commands * 100, 1)
                    if total_commands > 0
                    else 0
                ),
                "phases": [
                    "Basic Commands",
                    "AI Chat Features",
                    "Project Operations",
                    "Tool Operations",
                    "Interactive Features",
                    "Advanced Tool Calls",
                    "Memory Operations",
                ],
                "detailed_results": self.demo_results,
            }
        }

        # Save report
        report_file = self.project_root / "cli_demo_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("=" * 60)
        logger.info("🎯 CLI DEMONSTRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total Commands: {total_commands}")
        logger.info(f"Successful: {successful_commands}")
        logger.info(f"Success Rate: {report['cli_demo_report']['success_rate']}%")
        logger.info(f"Report saved: {report_file}")

        # Show successful commands
        if successful_commands > 0:
            logger.info("\n✅ Successful Commands:")
            for result in self.demo_results:
                if result["success"]:
                    logger.info(f"  ✓ {result['description']} ({result['duration']}s)")

        # Show failed commands
        failed_commands = [r for r in self.demo_results if not r["success"]]
        if failed_commands:
            logger.info(f"\n❌ Failed Commands ({len(failed_commands)}):")
            for result in failed_commands:
                logger.info(f"  ✗ {result['description']}: {result['stderr'][:50]}...")

        logger.info("=" * 60)

        return report

    def run_full_demo(self):
        """Run complete CLI demonstration."""
        logger.info("🚀 Starting Plato CLI Demonstration")
        logger.info(f"Project: {self.project_root}")
        logger.info(f"Python: {self.venv_python}")

        try:
            # Verify setup
            if not self.venv_python.exists():
                logger.error(f"Python environment not found: {self.venv_python}")
                return False

            # Run all demo phases
            self.demo_basic_commands()
            self.demo_ai_chat()
            self.demo_project_operations()
            self.demo_tool_operations()
            self.demo_interactive_features()
            self.demo_advanced_tool_calls()
            self.demo_memory_operations()

            # Generate report
            report = self.generate_report()

            return report["cli_demo_report"]["success_rate"] > 50

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            return False


def main():
    """Main demonstration entry point."""
    demo = PlatoCLIDemo()
    success = demo.run_full_demo()

    print(f"\n{'✅ CLI DEMO SUCCESSFUL' if success else '❌ CLI DEMO FAILED'}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
