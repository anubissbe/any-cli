#!/usr/bin/env python3
"""Test AI provider connections for Plato server."""

import asyncio
import logging
import os
import sys
from typing import List, Tuple

import openai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_qwen_local(base_urls: List[str]) -> Tuple[bool, str, str]:
    """Test connection to local Qwen model."""
    for base_url in base_urls:
        try:
            # Test with /v1 endpoint first (Ollama format)
            for endpoint in [f"{base_url}/v1", base_url]:
                try:
                    logger.info(f"Testing Qwen connection to: {endpoint}")

                    # Test basic connectivity first
                    try:
                        response = requests.get(f"{endpoint}/models", timeout=5)
                        if response.status_code == 200:
                            logger.info(f"✓ Models endpoint accessible at {endpoint}")
                            models = response.json()
                            if isinstance(models, dict) and "data" in models:
                                model_names = [
                                    m.get("id", "unknown") for m in models["data"]
                                ]
                                logger.info(f"Available models: {model_names}")
                            elif isinstance(models, list):
                                model_names = [
                                    m.get("name", m.get("id", "unknown"))
                                    for m in models
                                ]
                                logger.info(f"Available models: {model_names}")
                    except Exception as e:
                        logger.warning(f"Models endpoint not accessible: {e}")

                    # Test OpenAI client
                    client = openai.AsyncOpenAI(
                        base_url=endpoint, api_key="dummy-key", timeout=10.0
                    )

                    # Try a simple completion
                    response = await client.chat.completions.create(
                        model="/opt/models/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf",
                        messages=[
                            {"role": "user", "content": "Hello, respond with just 'OK'"}
                        ],
                        max_tokens=10,
                        temperature=0.1,
                    )

                    if response.choices and response.choices[0].message.content:
                        content = response.choices[0].message.content.strip()
                        logger.info(f"✓ Qwen local connection successful at {endpoint}")
                        logger.info(f"Test response: {content}")
                        return True, endpoint, content

                except Exception as e:
                    logger.warning(f"Failed to connect to {endpoint}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error testing {base_url}: {e}")
            continue

    return False, "", "Connection failed"


async def test_openrouter() -> Tuple[bool, str]:
    """Test OpenRouter connection."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False, "No API key found"

    try:
        client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=api_key, timeout=10.0
        )

        # Test with a free model
        response = await client.chat.completions.create(
            model="qwen/qwen3-coder:free",
            messages=[{"role": "user", "content": "Hello, respond with just 'OK'"}],
            max_tokens=10,
            temperature=0.1,
        )

        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content.strip()
            logger.info(f"✓ OpenRouter connection successful")
            logger.info(f"Test response: {content}")
            return True, content

    except Exception as e:
        logger.error(f"OpenRouter connection failed: {e}")
        return False, str(e)

    return False, "Unknown error"


async def test_gemini() -> Tuple[bool, str]:
    """Test Gemini connection."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "No API key found"

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async("Hello, respond with just 'OK'")

        if response.text:
            logger.info(f"✓ Gemini connection successful")
            logger.info(f"Test response: {response.text.strip()}")
            return True, response.text.strip()

    except Exception as e:
        logger.error(f"Gemini connection failed: {e}")
        return False, str(e)

    return False, "Unknown error"


async def main():
    """Main test function."""
    logger.info("Testing AI provider connections...")

    results = {}

    # Test Qwen local - try common ports and IPs
    qwen_urls = [
        "http://192.168.1.28:11434",  # Primary target
        "http://192.168.1.28:8000",  # Alternative port
        "http://localhost:11434",  # Local fallback
        "http://localhost:8000",  # Local alternative
    ]

    success, endpoint, response = await test_qwen_local(qwen_urls)
    results["qwen_local"] = {
        "success": success,
        "endpoint": endpoint,
        "response": response,
    }

    # Test OpenRouter
    success, response = await test_openrouter()
    results["openrouter"] = {"success": success, "response": response}

    # Test Gemini
    success, response = await test_gemini()
    results["gemini"] = {"success": success, "response": response}

    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("AI Provider Connection Test Results:")
    logger.info("=" * 50)

    for provider, result in results.items():
        status = "✓ WORKING" if result["success"] else "✗ FAILED"
        logger.info(f"{provider.upper()}: {status}")
        if result["success"] and "endpoint" in result:
            logger.info(f"  Endpoint: {result['endpoint']}")
        if result["response"]:
            logger.info(f"  Response: {result['response']}")

    # Check if at least one provider is working
    working_providers = [p for p, r in results.items() if r["success"]]
    if working_providers:
        logger.info(
            f"\n✓ {len(working_providers)} provider(s) working: {', '.join(working_providers)}"
        )
        return 0
    else:
        logger.error("\n✗ No AI providers are working!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
