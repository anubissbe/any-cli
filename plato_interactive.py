#!/usr/bin/env python3
"""Standalone launcher for Plato Interactive CLI."""

import asyncio
import sys
from pathlib import Path

# Add the plato package to the Python path
plato_dir = Path(__file__).parent
sys.path.insert(0, str(plato_dir))

from plato.interactive_cli import main as interactive_main

if __name__ == "__main__":
    # Get server URL from command line args or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    print(f"Starting Plato Interactive CLI...")
    print(f"Server URL: {server_url}")
    print()

    try:
        asyncio.run(interactive_main(server_url))
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
