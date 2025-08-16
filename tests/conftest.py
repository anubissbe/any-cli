"""Test configuration and fixtures for Plato tests."""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient

from plato.core.ai_router import AIRouter
from plato.core.context_manager import ContextManager
from plato.core.mcp_manager import MCPManager
from plato.integrations.serena_mcp import SerenaMCPClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Create a temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)

        # Create some test files
        (workspace / "test_project").mkdir()
        (workspace / "test_project" / "main.py").write_text(
            'def hello_world():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    hello_world()\n'
        )
        (workspace / "test_project" / "utils.py").write_text(
            "def add_numbers(a: int, b: int) -> int:\n    return a + b\n\ndef multiply(x: int, y: int) -> int:\n    return x * y\n"
        )
        (workspace / "test_project" / "requirements.txt").write_text(
            "pytest>=7.4.0\nrequests>=2.31.0\n"
        )

        # Create TypeScript test files
        (workspace / "test_ts_project").mkdir()
        (workspace / "test_ts_project" / "package.json").write_text(
            '{"name": "test-project", "version": "1.0.0", "dependencies": {"express": "^4.18.0"}}'
        )
        (workspace / "test_ts_project" / "index.ts").write_text(
            "interface User {\n  name: string;\n  age: number;\n}\n\nexport function createUser(name: string, age: number): User {\n  return { name, age };\n}\n"
        )

        yield workspace


@pytest.fixture
def test_config() -> dict:
    """Provide test configuration."""
    return {
        # Use fake API keys for testing
        "anthropic_api_key": "test-anthropic-key",
        "openai_api_key": "test-openai-key",
        "gemini_api_key": "test-gemini-key",
        "openrouter_api_key": "test-openrouter-key",
        "qwen_base_url": "http://localhost:8000",
        # MCP configuration
        "mcp_servers": {
            "serena": {"enabled": True, "url": "http://localhost:8765", "timeout": 10}
        },
        # Context settings for testing
        "context": {
            "max_tokens": 1000,
            "preserve_tokens": 200,
            "compression_ratio": 0.5,
        },
    }


@pytest_asyncio.fixture
async def ai_router(test_config: dict) -> AsyncGenerator[AIRouter, None]:
    """Create an AI router for testing."""
    router = AIRouter(config=test_config)
    # Give it a moment to initialize clients
    await asyncio.sleep(0.1)
    yield router


@pytest_asyncio.fixture
async def context_manager(test_config: dict) -> AsyncGenerator[ContextManager, None]:
    """Create a context manager for testing."""
    from plato.core.context_manager import ContextWindow

    window = ContextWindow(
        max_tokens=test_config["context"]["max_tokens"],
        preserve_tokens=test_config["context"]["preserve_tokens"],
        compression_ratio=test_config["context"]["compression_ratio"],
    )

    manager = ContextManager(window)
    yield manager


@pytest_asyncio.fixture
async def mcp_manager() -> AsyncGenerator[MCPManager, None]:
    """Create an MCP manager for testing."""
    manager = MCPManager()
    yield manager


@pytest_asyncio.fixture
async def serena_client() -> AsyncGenerator[SerenaMCPClient, None]:
    """Create a Serena MCP client for testing."""
    client = SerenaMCPClient(host="localhost", port=8765, timeout=10)

    # Check if Serena is actually running
    if await client.health_check():
        yield client
    else:
        pytest.skip("Serena MCP server not available at localhost:8765")

    await client.disconnect()


@pytest_asyncio.fixture
async def plato_server_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for Plato server testing."""
    async with AsyncClient(base_url="http://localhost:8080", timeout=10.0) as client:
        # Check if server is running
        try:
            response = await client.get("/health")
            if response.status_code != 200:
                pytest.skip("Plato server not available at localhost:8080")
        except Exception:
            pytest.skip("Plato server not available at localhost:8080")

        yield client


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing."""
    return '''def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def factorial(n: int) -> int:
    """Calculate the factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    """A simple calculator class."""
    
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''


@pytest.fixture
def sample_typescript_code() -> str:
    """Sample TypeScript code for testing."""
    return """interface Person {
    name: string;
    age: number;
    email?: string;
}

class UserManager {
    private users: Person[] = [];
    
    addUser(user: Person): void {
        this.users.push(user);
    }
    
    findUserByName(name: string): Person | undefined {
        return this.users.find(user => user.name === name);
    }
    
    getUserCount(): number {
        return this.users.length;
    }
}

export function createPerson(name: string, age: number, email?: string): Person {
    return { name, age, email };
}

export { UserManager, Person };
"""


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow


# Skip conditions
def requires_serena():
    """Skip test if Serena MCP server is not available."""
    try:
        import httpx

        response = httpx.get("http://localhost:8765/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def requires_plato_server():
    """Skip test if Plato server is not available."""
    try:
        import httpx

        response = httpx.get("http://localhost:8080/health", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


# Custom skip decorators
skip_if_no_serena = pytest.mark.skipif(
    not requires_serena(), reason="Serena MCP server not available"
)

skip_if_no_plato_server = pytest.mark.skipif(
    not requires_plato_server(), reason="Plato server not available"
)
