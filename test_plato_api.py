#!/usr/bin/env python3
"""Test Plato API endpoints."""

import asyncio
import json
import logging
import sys

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8080"


async def test_health():
    """Test health endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()
            data = response.json()
            logger.info(f"Health Status: {data['status']}")
            logger.info(f"AI Providers: {data['ai_providers']}")
            logger.info(f"MCP Servers: {data['mcp_servers']}")
            return data["ai_providers"]
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {}


async def test_chat(
    provider, message="Hello! What AI model are you? Please respond briefly."
):
    """Test chat with specific provider."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "message": message,
                "task_type": "chat",
                "preferred_provider": provider,
            }

            logger.info(f"Testing chat with {provider}...")
            response = await client.post(f"{BASE_URL}/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            logger.info(f"✓ {provider} responded:")
            logger.info(f"  Provider used: {data['provider']}")
            logger.info(f"  Tokens used: {data['tokens_used']}")
            logger.info(f"  Response: {data['message'][:200]}...")

            return True, data

        except Exception as e:
            logger.error(f"✗ Chat with {provider} failed: {e}")
            return False, str(e)


async def test_auto_routing(message="What's 2+2? Respond briefly."):
    """Test automatic provider routing."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            payload = {
                "message": message,
                "task_type": "chat",
                # No preferred_provider - let router choose
            }

            logger.info("Testing automatic provider routing...")
            response = await client.post(f"{BASE_URL}/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            logger.info(f"✓ Auto-routing selected: {data['provider']}")
            logger.info(f"  Response: {data['message'][:100]}...")

            return True, data

        except Exception as e:
            logger.error(f"✗ Auto-routing failed: {e}")
            return False, str(e)


async def main():
    """Main test function."""
    logger.info("Testing Plato AI orchestration system...")

    # Test health first
    providers = await test_health()
    if not providers:
        logger.error("Health check failed, aborting tests")
        return 1

    # Test each working provider
    working_providers = [name for name, status in providers.items() if status]
    if not working_providers:
        logger.error("No working AI providers found")
        return 1

    logger.info(
        f"Testing {len(working_providers)} working providers: {working_providers}"
    )

    results = {}
    for provider in working_providers:
        success, data = await test_chat(provider)
        results[provider] = success

    # Test auto-routing
    auto_success, auto_data = await test_auto_routing()
    results["auto_routing"] = auto_success

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Results:")
    logger.info("=" * 50)

    for test, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{test}: {status}")

    passed = sum(1 for success in results.values() if success)
    total = len(results)
    logger.info(f"\nOverall: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
