#!/usr/bin/env python3
"""
Plato Binary Launcher
Standalone binary entry point that launches the interactive Claude Code-like interface by default.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add the plato package to the Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))


def main():
    """Main entry point for the Plato binary."""
    # Import Plato modules after path setup
    try:
        from plato.cli import app as cli_app
        from plato.interactive_cli import main as interactive_main
    except ImportError as e:
        print(f"Error: Failed to import Plato modules: {e}", file=sys.stderr)
        print("Make sure Plato is properly installed.", file=sys.stderr)
        sys.exit(1)

    # Check if no arguments provided or if it's an interactive request
    if len(sys.argv) == 1 or (
        len(sys.argv) == 2 and sys.argv[1] in ["interactive", "--interactive"]
    ):
        # Default to interactive mode
        print("🚀 Starting Plato Interactive CLI...")
        print("   Use /help for commands or Ctrl+C to exit")
        print()
        try:
            # Default server URL
            server_url = "http://localhost:8080"
            asyncio.run(interactive_main(server_url))
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Handle --version flag specially
    if len(sys.argv) == 2 and sys.argv[1] in ["--version", "-v", "version"]:
        print("Plato AI Orchestration System v0.1.0")
        return

    # Handle --help flag specially
    if len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h", "help"]:
        print(
            """Plato AI Orchestration System - Claude Code-like Interactive Interface

Usage:
  plato [COMMAND] [OPTIONS]

Commands:
  interactive         Start interactive chat session (default)
  chat MESSAGE        Send a single chat message
  health              Check server health
  tools               List available tools
  analyze PATH        Analyze code with Serena
  --version, -v       Show version information
  --help, -h          Show this help message

Examples:
  plato                     # Start interactive interface (default)
  plato interactive         # Start interactive interface explicitly
  plato chat "Hello"        # Send single chat message
  plato health              # Check server health
  plato tools               # List available tools
  plato --version           # Show version

For more detailed help in interactive mode, type '/help' once started.
        """
        )
        return

    # For all other commands, delegate to the original CLI
    try:
        cli_app()
    except SystemExit:
        pass  # Normal CLI exit
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
