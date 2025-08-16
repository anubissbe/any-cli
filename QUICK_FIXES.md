# Quick Fixes for Plato Test Suite

## Fix 1: AIRouter Event Loop Issue (CRITICAL)

The primary issue blocking all tests is in `plato/core/ai_router.py` line 110:

### Problem
```python
def __init__(self):
    asyncio.create_task(self._init_clients())  # Fails - no event loop
```

### Quick Fix
Replace the constructor initialization with a lazy initialization pattern:

```python
def __init__(self):
    self._clients = {}
    self._initialized = False

async def _ensure_initialized(self):
    if not self._initialized:
        await self._init_clients()
        self._initialized = True

async def chat(self, request: AIRequest) -> AIResponse:
    await self._ensure_initialized()  # Add this line at start
    # ... rest of existing method
```

## Fix 2: Add Unit Test Markers

Add markers to test_basic.py:

```python
import pytest

@pytest.mark.unit
class TestAIRouter:
    # existing tests...

@pytest.mark.unit  
class TestContextManager:
    # existing tests...

@pytest.mark.unit
class TestMCPManager:
    # existing tests...
```

## Fix 3: Mock Dependencies in Unit Tests

Update conftest.py to provide working mocks:

```python
@pytest.fixture
def ai_router():
    """Provide a mocked AI router for unit tests."""
    router = AIRouter()
    router._clients = {
        AIProvider.CLAUDE: AsyncMock(),
        AIProvider.GPT4: AsyncMock(),
        AIProvider.GPT3_5: AsyncMock()
    }
    router._initialized = True
    return router
```

## Apply Quick Fix

To test the fix, modify the AIRouter class temporarily: