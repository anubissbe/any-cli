"""Tests for MCP connection handling and WebSocket stability."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from websockets.exceptions import ConnectionClosed, ConnectionClosedError

from plato.core.mcp_manager import (
    MCPManager,
    MCPServerConfig,
    MCPTransport,
    STDIOMCPConnection,
    SSEMCPConnection,
    WebSocketMCPConnection,
    MCPResponse,
)


class TestMCPConnectionHandling:
    """Test MCP connection handling and error recovery."""

    @pytest.fixture
    def stdio_config(self):
        """STDIO MCP server configuration."""
        return MCPServerConfig(
            name="test-stdio",
            transport=MCPTransport.STDIO,
            command=["python", "-m", "test_server"],
            timeout=5,
            retry_attempts=3,
        )

    @pytest.fixture
    def sse_config(self):
        """SSE MCP server configuration."""
        return MCPServerConfig(
            name="test-sse",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            timeout=10,
        )

    @pytest.fixture
    def websocket_config(self):
        """WebSocket MCP server configuration."""
        return MCPServerConfig(
            name="test-ws",
            transport=MCPTransport.WEBSOCKET,
            url="ws://localhost:8766/mcp",
            timeout=15,
        )

    @pytest.mark.asyncio
    async def test_stdio_connection_failure_handling(self, stdio_config):
        """Test STDIO connection failure and recovery."""
        connection = STDIOMCPConnection(stdio_config)

        # Mock subprocess creation failure
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_subprocess.side_effect = OSError("Command not found")

            # Connection should fail gracefully
            result = await connection.connect()
            assert result is False
            assert not connection.connected

    @pytest.mark.asyncio
    async def test_stdio_connection_timeout_handling(self, stdio_config):
        """Test STDIO connection timeout handling."""
        connection = STDIOMCPConnection(stdio_config)

        # Mock slow subprocess
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.stdin = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Mock a hanging initialization
            async def hanging_send(*args, **kwargs):
                await asyncio.sleep(10)  # Longer than timeout

            mock_process.stdin.write = MagicMock()
            mock_process.stdin.drain = hanging_send

            # Should timeout and fail
            with pytest.raises(Exception):
                await connection.connect()

    @pytest.mark.asyncio
    async def test_stdio_process_cleanup(self, stdio_config):
        """Test proper cleanup of STDIO processes."""
        connection = STDIOMCPConnection(stdio_config)

        # Mock successful connection
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.stdin = AsyncMock()
            mock_process.stdout = AsyncMock()
            mock_process.stderr = AsyncMock()
            mock_process.terminate = AsyncMock()
            mock_process.kill = AsyncMock()
            mock_process.wait = AsyncMock()
            mock_subprocess.return_value = mock_process

            # Simulate connection
            connection.process = mock_process
            connection.connected = True
            connection._read_task = AsyncMock()

            # Test cleanup
            await connection.disconnect()

            # Verify cleanup was called
            mock_process.terminate.assert_called_once()
            mock_process.wait.assert_called()

    @pytest.mark.asyncio
    async def test_sse_connection_failure_recovery(self, sse_config):
        """Test SSE connection failure and retry logic."""
        connection = SSEMCPConnection(sse_config)

        # Mock HTTP client failure
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # First call fails, second succeeds
            mock_client.get.side_effect = [
                Exception("Connection refused"),
                AsyncMock(status_code=200),
            ]

            # First attempt should fail
            result = await connection.connect()
            assert result is False

            # Reset for second attempt
            mock_client.get.side_effect = [AsyncMock(status_code=200)]

            # Second attempt should succeed
            result = await connection.connect()
            assert result is True

    @pytest.mark.asyncio
    async def test_websocket_connection_stability(self, websocket_config):
        """Test WebSocket connection stability and reconnection."""
        connection = WebSocketMCPConnection(websocket_config)

        # Mock websockets
        with patch("websockets.connect") as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket

            # Test successful connection
            result = await connection.connect()
            assert result is True
            assert connection.connected

    @pytest.mark.asyncio
    async def test_websocket_connection_drops(self, websocket_config):
        """Test handling of WebSocket connection drops."""
        connection = WebSocketMCPConnection(websocket_config)

        with patch("websockets.connect") as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket

            # Simulate connection drop during read
            async def mock_read_responses():
                # Simulate some messages then connection drop
                yield json.dumps({"id": "1", "result": "test"})
                raise ConnectionClosed(None, None)

            mock_websocket.__aiter__ = lambda: mock_read_responses()

            # Connect successfully
            await connection.connect()

            # Start reading task which should handle connection drop
            connection._read_task = asyncio.create_task(connection._read_responses())

            # Wait for task to complete (due to connection drop)
            await asyncio.sleep(0.1)

            # Task should complete without unhandled exceptions
            assert connection._read_task.done()

    @pytest.mark.asyncio
    async def test_mcp_manager_connection_resilience(self):
        """Test MCP manager handling multiple connection failures."""
        manager = MCPManager()

        # Add multiple servers with different transports
        configs = [
            MCPServerConfig(
                name="failing-stdio",
                transport=MCPTransport.STDIO,
                command=["nonexistent-command"],
            ),
            MCPServerConfig(
                name="failing-sse",
                transport=MCPTransport.SSE,
                url="http://localhost:9999",  # Non-existent port
            ),
            MCPServerConfig(
                name="failing-ws",
                transport=MCPTransport.WEBSOCKET,
                url="ws://localhost:9998/mcp",  # Non-existent port
            ),
        ]

        for config in configs:
            manager.add_server(config)

        # Attempt to connect all - should handle failures gracefully
        results = await manager.connect_all()

        # All should fail but not crash
        assert all(not success for success in results.values())
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_request_timeout_handling(self, sse_config):
        """Test request timeout handling."""
        connection = SSEMCPConnection(sse_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock successful connection
            mock_client.get.return_value = AsyncMock(status_code=200)
            await connection.connect()

            # Mock hanging request
            async def hanging_request(*args, **kwargs):
                await asyncio.sleep(20)  # Longer than timeout

            mock_client.post = hanging_request

            # Request should timeout
            with pytest.raises(Exception) as exc_info:
                await connection.send_request("test_method", {"param": "value"})

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, sse_config):
        """Test handling of concurrent requests."""
        connection = SSEMCPConnection(sse_config)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client

            # Mock successful connection
            mock_client.get.return_value = AsyncMock(status_code=200)
            await connection.connect()

            # Mock request responses
            async def mock_post(*args, **kwargs):
                response = AsyncMock()
                response.raise_for_status = MagicMock()
                response.json.return_value = {
                    "id": kwargs.get("json", {}).get("id"),
                    "result": "success",
                }
                return response

            mock_client.post = mock_post

            # Send multiple concurrent requests
            tasks = [
                connection.send_request("test_method", {"request": i}) for i in range(5)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            assert len(results) == 5
            assert all(isinstance(r, MCPResponse) for r in results)

    @pytest.mark.asyncio
    async def test_tool_call_with_connection_recovery(self):
        """Test tool calling with automatic connection recovery."""
        manager = MCPManager()

        # Add a mock server
        config = MCPServerConfig(
            name="test-server",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
        )
        manager.add_server(config)

        # Mock the connection
        mock_connection = AsyncMock()
        mock_connection.connected = False
        mock_connection.config = config
        mock_connection.connect.return_value = True
        mock_connection.call_tool.return_value = {"result": "success"}

        manager.servers["test-server"] = mock_connection

        # Add a mock tool
        from plato.core.mcp_manager import MCPTool, MCPToolType

        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            input_schema={},
            server="test-server",
            tool_type=MCPToolType.FUNCTION,
        )
        manager.tools["test-server.test_tool"] = tool

        # Call tool - should trigger reconnection
        result = await manager.call_tool("test_tool", {"param": "value"})

        # Verify connection was attempted and tool was called
        mock_connection.connect.assert_called_once()
        mock_connection.call_tool.assert_called_once()
        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self, websocket_config):
        """Test that connections don't leak memory with failed requests."""
        connection = WebSocketMCPConnection(websocket_config)

        with patch("websockets.connect") as mock_connect:
            mock_websocket = AsyncMock()
            mock_connect.return_value = mock_websocket

            await connection.connect()

            # Simulate many failed requests
            for i in range(100):
                try:
                    # This should timeout and clean up properly
                    await asyncio.wait_for(
                        connection.send_request("test", {}),
                        timeout=0.01,  # Very short timeout
                    )
                except asyncio.TimeoutError:
                    pass

            # Pending requests should be cleaned up
            assert len(connection.pending_requests) == 0

    @pytest.mark.asyncio
    async def test_server_status_reporting(self):
        """Test accurate server status reporting."""
        manager = MCPManager()

        # Add servers with different states
        configs = [
            MCPServerConfig(name="connected", transport=MCPTransport.SSE),
            MCPServerConfig(name="disconnected", transport=MCPTransport.SSE),
            MCPServerConfig(name="disabled", transport=MCPTransport.SSE, enabled=False),
        ]

        for config in configs:
            manager.add_server(config)

        # Mock connection states
        manager.servers["connected"].connected = True
        manager.servers["disconnected"].connected = False

        # Add some tools
        from plato.core.mcp_manager import MCPTool, MCPToolType

        manager.tools["connected.tool1"] = MCPTool(
            name="tool1", description="", input_schema={}, server="connected"
        )
        manager.tools["connected.tool2"] = MCPTool(
            name="tool2", description="", input_schema={}, server="connected"
        )

        status = manager.get_server_status()

        assert status["connected"]["connected"] is True
        assert status["connected"]["tools_count"] == 2
        assert status["disconnected"]["connected"] is False
        assert status["disabled"]["enabled"] is False
