#!/usr/bin/env python3
"""Generate secure API keys for Plato API server."""

import sys
from plato.core.security import generate_api_key, hash_api_key


def main():
    """Generate a new API key pair."""
    print("Generating new API key for Plato API server...")
    print("-" * 50)

    key_id, key_secret = generate_api_key()

    print("\nAPI Key Generated Successfully!")
    print("=" * 50)
    print(f"\nKey ID: {key_id}")
    print(f"Key Secret: {key_secret}")
    print(f"\nFull API Key (for clients): {key_id}:{key_secret}")
    print(f"\nHashed Key (for .env file): {key_id}:{hash_api_key(key_secret)}")

    print("\n" + "=" * 50)
    print("\nTo use this key:")
    print("1. Add to your .env file:")
    print(f"   PLATO_API_KEYS={key_id}:{hash_api_key(key_secret)}")
    print("   PLATO_REQUIRE_API_KEY=true")
    print("\n2. In API requests, add header:")
    print(f"   X-API-Key: {key_id}:{key_secret}")

    print("\n⚠️  IMPORTANT:")
    print("- Save the key secret securely - it cannot be recovered!")
    print("- Only store the hashed version in configuration files")
    print("- Never commit API keys to version control")
    print("- Rotate keys regularly for better security")


if __name__ == "__main__":
    main()
