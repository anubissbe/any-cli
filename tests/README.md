# Plato Test Suite

This directory contains comprehensive tests for the Plato AI orchestration system. The tests verify that all components work correctly individually and together as a complete system.

## Test Structure

### Test Categories

1. **Unit Tests** (`test_basic.py`)
   - Fast, isolated tests with no external dependencies
   - Test individual components like AI router, context manager, MCP manager
   - Use mocked dependencies to avoid external API calls

2. **Integration Tests**
   - **AI Router** (`test_ai_router_integration.py`) - Provider selection, fallback, chat functionality
   - **MCP Manager** (`test_mcp_manager_integration.py`) - Server management, tool discovery, execution
   - **Serena MCP** (`test_serena_integration.py`) - Real LSP operations with Serena server
   - **API** (`test_api_integration.py`) - FastAPI endpoints and WebSocket support
   - **CLI** (`test_cli_integration.py`) - Command-line interface functionality

3. **End-to-End Tests** (`test_end_to_end.py`)
   - Complete workflows using all components together
   - AI-powered code analysis with context management
   - Real integration between Serena, AI providers, and context

### Test Configuration

- **`conftest.py`** - Shared fixtures and test configuration
- **`test_config.yaml`** - Environment-specific test settings
- **`run_tests.py`** - Comprehensive test runner with reporting

## Prerequisites

### Required Services

1. **Serena MCP Server** (for integration tests)
   ```bash
   # Start Serena MCP server
   ./start_serena_mcp.sh start
   
   # Verify it's running
   curl http://localhost:8765/health
   ```

2. **Plato Server** (for API tests)
   ```bash
   # Start Plato server
   python -m plato.server.api
   
   # Verify it's running
   curl http://localhost:8080/health
   ```

### Python Dependencies

```bash
# Install test dependencies
pip install -e .[dev]

# Or install manually
pip install pytest pytest-asyncio pytest-cov httpx rich typer
```

## Running Tests

### Quick Start

```bash
# Run all tests with the test runner
python tests/run_tests.py

# Check prerequisites only
python tests/run_tests.py --check-prereqs

# Run only unit tests (no external dependencies)
python tests/run_tests.py --unit-only

# Run only integration tests
python tests/run_tests.py --integration-only

# Skip slow end-to-end tests
python tests/run_tests.py --no-e2e
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_serena_integration.py

# Run tests with specific markers
pytest -m "unit"                    # Only unit tests
pytest -m "integration"             # Only integration tests
pytest -m "not slow"               # Skip slow tests
pytest -m "integration and not slow" # Integration but not slow

# Run with coverage
pytest --cov=plato --cov-report=html

# Run specific test method
pytest tests/test_basic.py::TestAIRouter::test_provider_selection_by_task
```

### Test Markers

- `unit` - Fast tests with no external dependencies
- `integration` - Tests that may use external services
- `slow` - Long-running tests (>30 seconds)
- `skip_if_no_serena` - Automatically skipped if Serena not available
- `skip_if_no_plato_server` - Automatically skipped if Plato server not available

## Test Environments

The test suite supports different environments via `test_config.yaml`:

### Local Development
```bash
# Use real API keys if available, longer timeouts for debugging
TEST_ENV=local python tests/run_tests.py
```

### CI/CD
```bash
# Mock all external dependencies, shorter timeouts
TEST_ENV=ci python tests/run_tests.py
```

### Mock Only
```bash
# No external dependencies at all
TEST_ENV=mock python tests/run_tests.py
```

### Performance Testing
```bash
# Large context sizes, longer timeouts
TEST_ENV=performance python tests/run_tests.py
```

## Test Data

Tests use temporary workspaces with sample projects:

- **Python Project** - Simple Python files with functions and classes
- **TypeScript Project** - TypeScript interfaces and classes
- **Multi-language Project** - Mixed Python, TypeScript, JavaScript

Sample code includes:
- Fibonacci and factorial functions
- Calculator class with error handling
- TypeScript interfaces and classes
- Various code patterns for analysis

## Writing New Tests

### Test Structure

```python
import pytest
from tests.conftest import skip_if_no_serena

@pytest.mark.integration
@skip_if_no_serena
class TestNewFeature:
    """Test new feature functionality."""
    
    async def test_feature_works(self, fixture_name):
        """Test that the feature works as expected."""
        # Arrange
        # Act
        # Assert
```

### Using Fixtures

Common fixtures available:
- `temp_workspace` - Temporary directory with sample projects
- `serena_client` - Connected Serena MCP client
- `ai_router` - AI router with test configuration
- `context_manager` - Context manager with test settings
- `plato_server_client` - HTTP client for Plato server

### Mocking External Dependencies

```python
from unittest.mock import AsyncMock, MagicMock

async def test_with_mocked_ai(ai_router):
    # Mock AI client to avoid real API calls
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Mocked response")]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    
    ai_router._clients[AIProvider.CLAUDE] = mock_client
    
    # Test continues with mocked client...
```

## Test Reports

The test runner generates comprehensive reports:

1. **Prerequisites Check** - Verifies all required services are running
2. **Test Results Table** - Shows status, duration, and notes for each category
3. **Coverage Report** - HTML coverage report in `htmlcov/`
4. **JUnit XML** - Test results in XML format for CI systems

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=plato --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Continuous Integration

For CI systems, use the CI configuration:

```bash
# Install dependencies
pip install -e .[dev]

# Start required services (if available)
./start_serena_mcp.sh start || echo "Serena not available"

# Run tests with CI configuration
TEST_ENV=ci python tests/run_tests.py --no-e2e
```

The CI configuration:
- Disables real AI provider calls
- Uses shorter timeouts
- Skips tests requiring unavailable services
- Generates JUnit XML for CI reporting

## Troubleshooting

### Common Issues

1. **Serena MCP Server Not Available**
   ```bash
   # Check if running
   curl http://localhost:8765/health
   
   # Start if needed
   ./start_serena_mcp.sh start
   
   # Check logs
   ./start_serena_mcp.sh logs
   ```

2. **Plato Server Not Available**
   ```bash
   # Start server
   python -m plato.server.api
   
   # Or check if already running
   lsof -i :8080
   ```

3. **Port Conflicts**
   ```bash
   # Kill processes on required ports
   kill -9 $(lsof -t -i:8765)  # Serena
   kill -9 $(lsof -t -i:8080)  # Plato server
   ```

4. **Import Errors**
   ```bash
   # Install in development mode
   pip install -e .[dev]
   
   # Or install missing dependencies
   pip install pytest pytest-asyncio httpx
   ```

5. **Tests Timeout**
   - Increase timeouts in `test_config.yaml`
   - Check for hanging processes
   - Use `--no-e2e` to skip slow tests

### Debug Mode

For debugging test failures:

```bash
# Run with verbose output and no capture
pytest -v -s tests/test_specific.py

# Run single test with debugging
pytest --pdb tests/test_file.py::test_method

# Print variables during test
pytest -v --capture=no tests/test_file.py
```

## Test Metrics

The test suite tracks:
- **Test Coverage** - Code coverage percentage
- **Test Duration** - Time taken for each test category
- **Success Rate** - Percentage of tests passing
- **Prerequisites** - Which services are available

Example metrics:
- Unit tests: ~30 tests, <1 minute
- Integration tests: ~50 tests, 2-5 minutes
- End-to-end tests: ~10 tests, 5-10 minutes
- Total coverage target: >80%

## Contributing

When adding new features to Plato:

1. **Write tests first** (TDD approach)
2. **Add unit tests** for isolated functionality
3. **Add integration tests** for component interaction
4. **Update fixtures** if new test data is needed
5. **Update this README** if new test categories are added

### Test Guidelines

- Tests should be **fast** and **reliable**
- Use **descriptive test names** that explain the scenario
- **Mock external dependencies** in unit tests
- **Use real dependencies** in integration tests (when available)
- **Clean up resources** after tests (files, connections, etc.)
- **Handle test failures gracefully** (no hanging processes)

## Architecture

The test architecture mirrors the Plato system architecture:

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_config.yaml         # Environment-specific settings
├── run_tests.py             # Test runner with reporting
├── test_basic.py            # Unit tests
├── test_*_integration.py    # Integration tests per component
├── test_end_to_end.py       # Complete system workflows
└── README.md               # This documentation
```

This structure ensures:
- **Separation of concerns** - Each test file focuses on one component
- **Reusable fixtures** - Common setup shared across tests
- **Environment flexibility** - Different configurations for different contexts
- **Comprehensive reporting** - Detailed feedback on test results