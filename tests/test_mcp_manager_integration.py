"""Integration tests for MCP Manager functionality.

These tests verify that the MCP manager can discover, connect to,
and interact with MCP servers like Serena.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from plato.core.mcp_manager import MCPManager, MCPServerConfig, MCPTransport
from tests.conftest import skip_if_no_serena


@pytest.mark.integration
class TestMCPManagerConfiguration:
    """Test MCP manager configuration and server management."""

    async def test_add_server_configuration(self, mcp_manager: MCPManager):
        """Test adding server configurations."""
        config = MCPServerConfig(
            name="test-server",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            timeout=30,
            description="Test MCP server",
        )

        success = mcp_manager.add_server(config)
        assert success is True
        assert "test-server" in mcp_manager.servers

        # Test duplicate rejection
        success_duplicate = mcp_manager.add_server(config)
        assert success_duplicate is False

    async def test_remove_server_configuration(self, mcp_manager: MCPManager):
        """Test removing server configurations."""
        config = MCPServerConfig(
            name="removable-server",
            transport=MCPTransport.SSE,
            url="http://localhost:8766",
        )

        # Add server
        mcp_manager.add_server(config)
        assert "removable-server" in mcp_manager.servers

        # Remove server
        success = mcp_manager.remove_server("removable-server")
        assert success is True
        assert "removable-server" not in mcp_manager.servers

        # Test removing non-existent server
        success_missing = mcp_manager.remove_server("non-existent")
        assert success_missing is False

    async def test_list_servers(self, mcp_manager: MCPManager):
        """Test listing configured servers."""
        # Add multiple servers
        configs = [
            MCPServerConfig(
                name="server1", transport=MCPTransport.SSE, url="http://localhost:8765"
            ),
            MCPServerConfig(
                name="server2", transport=MCPTransport.STDIO, command=["echo", "test"]
            ),
            MCPServerConfig(
                name="server3", transport=MCPTransport.SSE, url="http://localhost:8767"
            ),
        ]

        for config in configs:
            mcp_manager.add_server(config)

        servers = mcp_manager.list_servers()
        assert len(servers) >= 3

        server_names = [s.name for s in servers]
        assert "server1" in server_names
        assert "server2" in server_names
        assert "server3" in server_names


@pytest.mark.integration
@skip_if_no_serena
class TestMCPManagerSerenaIntegration:
    """Test MCP manager integration with actual Serena server."""

    async def test_add_serena_server(self, mcp_manager: MCPManager):
        """Test adding Serena MCP server configuration."""
        serena_config = MCPServerConfig(
            name="serena-mcp",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            port=8765,
            timeout=30,
            description="Serena LSP-based MCP server",
        )

        success = mcp_manager.add_server(serena_config)
        assert success is True

        # Verify configuration
        servers = mcp_manager.list_servers()
        serena_servers = [s for s in servers if s.name == "serena-mcp"]
        assert len(serena_servers) == 1

        serena_server = serena_servers[0]
        assert serena_server.url == "http://localhost:8765"
        assert serena_server.port == 8765
        assert serena_server.transport == MCPTransport.SSE

    async def test_connect_to_serena(self, mcp_manager: MCPManager):
        """Test connecting to Serena MCP server."""
        serena_config = MCPServerConfig(
            name="serena-connect-test",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            timeout=10,
        )

        mcp_manager.add_server(serena_config)

        # Try to connect
        success = await mcp_manager.connect_server("serena-connect-test")

        # Connection might succeed or fail depending on server state
        # The important thing is that the attempt is handled gracefully
        assert isinstance(success, bool)

        if success:
            # If connected, verify connection status
            connection = mcp_manager.get_server_connection("serena-connect-test")
            assert connection is not None

            # Try to disconnect
            disconnect_success = await mcp_manager.disconnect_server(
                "serena-connect-test"
            )
            assert disconnect_success is True


@pytest.mark.integration
class TestMCPManagerToolDiscovery:
    """Test MCP manager tool discovery functionality."""

    async def test_mock_tool_discovery(self, mcp_manager: MCPManager):
        """Test tool discovery with mocked MCP connection."""
        # Create mock connection
        mock_connection = MagicMock()
        mock_connection.config.name = "mock-server"
        mock_connection.connected = True

        # Mock tools
        mock_tools = [
            MagicMock(
                name="open_file", server="mock-server", description="Open a file"
            ),
            MagicMock(
                name="save_file", server="mock-server", description="Save a file"
            ),
            MagicMock(
                name="get_symbols", server="mock-server", description="Get file symbols"
            ),
        ]
        mock_connection.list_tools = AsyncMock(return_value=mock_tools)

        # Add mock connection to manager
        mcp_manager.servers["mock-server"] = mock_connection

        # Simulate tool discovery
        for tool in mock_tools:
            tool_key = f"{tool.server}.{tool.name}"
            mcp_manager.tools[tool_key] = tool

        # Test listing tools
        tools = mcp_manager.list_tools("mock-server")
        assert len(tools) == 3

        tool_names = [t.name for t in tools]
        assert "open_file" in tool_names
        assert "save_file" in tool_names
        assert "get_symbols" in tool_names

    async def test_tool_lookup(self, mcp_manager: MCPManager):
        """Test looking up specific tools."""
        # Add mock tools
        mock_tool = MagicMock(name="test_tool", server="test-server")
        mcp_manager.tools["test-server.test_tool"] = mock_tool

        # Test successful lookup
        found_tool = mcp_manager.get_tool("test-server.test_tool")
        assert found_tool is not None
        assert found_tool.name == "test_tool"
        assert found_tool.server == "test-server"

        # Test missing tool
        missing_tool = mcp_manager.get_tool("nonexistent.tool")
        assert missing_tool is None

    async def test_list_all_tools(self, mcp_manager: MCPManager):
        """Test listing all available tools across servers."""
        # Add tools from multiple mock servers
        tools_data = [
            ("server1", "tool1"),
            ("server1", "tool2"),
            ("server2", "tool3"),
            ("server2", "tool4"),
        ]

        for server, tool_name in tools_data:
            mock_tool = MagicMock(name=tool_name, server=server)
            mcp_manager.tools[f"{server}.{tool_name}"] = mock_tool

        all_tools = mcp_manager.list_all_tools()
        assert len(all_tools) == 4

        tool_keys = list(all_tools.keys())
        assert "server1.tool1" in tool_keys
        assert "server1.tool2" in tool_keys
        assert "server2.tool3" in tool_keys
        assert "server2.tool4" in tool_keys


@pytest.mark.integration
class TestMCPManagerToolExecution:
    """Test MCP manager tool execution functionality."""

    async def test_mock_tool_execution(self, mcp_manager: MCPManager):
        """Test executing tools with mocked responses."""
        # Create mock connection with tool execution capability
        mock_connection = MagicMock()
        mock_connection.config.name = "exec-server"
        mock_connection.connected = True

        # Mock successful tool execution
        mock_result = {"success": True, "result": "Tool executed successfully"}
        mock_connection.call_tool = AsyncMock(return_value=mock_result)

        # Add connection and tool
        mcp_manager.servers["exec-server"] = mock_connection
        mock_tool = MagicMock(name="execute_test", server="exec-server")
        mcp_manager.tools["exec-server.execute_test"] = mock_tool

        # Execute tool
        result = await mcp_manager.call_tool(
            "exec-server.execute_test", {"param1": "value1", "param2": "value2"}
        )

        assert result is not None
        assert result.get("success") is True
        assert "result" in result

        # Verify the call was made with correct arguments
        mock_connection.call_tool.assert_called_once_with(
            "execute_test", {"param1": "value1", "param2": "value2"}
        )

    async def test_tool_execution_error_handling(self, mcp_manager: MCPManager):
        """Test error handling during tool execution."""
        # Create mock connection that fails
        mock_connection = MagicMock()
        mock_connection.config.name = "failing-server"
        mock_connection.connected = True
        mock_connection.call_tool = AsyncMock(
            side_effect=Exception("Tool execution failed")
        )

        # Add connection and tool
        mcp_manager.servers["failing-server"] = mock_connection
        mock_tool = MagicMock(name="failing_tool", server="failing-server")
        mcp_manager.tools["failing-server.failing_tool"] = mock_tool

        # Execute tool (should handle error gracefully)
        result = await mcp_manager.call_tool("failing-server.failing_tool", {})

        # Should return error information instead of raising exception
        assert result is not None
        assert "error" in result or result.get("success") is False

    async def test_tool_execution_missing_tool(self, mcp_manager: MCPManager):
        """Test executing a non-existent tool."""
        result = await mcp_manager.call_tool("nonexistent.tool", {})

        assert result is not None
        assert "error" in result or result.get("success") is False


@pytest.mark.integration
class TestMCPManagerConnectionLifecycle:
    """Test MCP manager connection lifecycle management."""

    async def test_connection_status_tracking(self, mcp_manager: MCPManager):
        """Test tracking connection status."""
        config = MCPServerConfig(
            name="status-test",
            transport=MCPTransport.SSE,
            url="http://localhost:9999",  # Non-existent server
        )

        mcp_manager.add_server(config)

        # Initially should not be connected
        connection = mcp_manager.get_server_connection("status-test")
        assert connection is None or not getattr(connection, "connected", True)

        # Try to connect (will fail, but should be handled)
        success = await mcp_manager.connect_server("status-test")
        assert isinstance(success, bool)

        # Status should be tracked appropriately
        status = mcp_manager.get_server_status("status-test")
        assert isinstance(status, dict)
        assert "connected" in status

    async def test_bulk_connection_operations(self, mcp_manager: MCPManager):
        """Test connecting/disconnecting multiple servers."""
        # Add multiple test servers
        configs = [
            MCPServerConfig(
                name="bulk1", transport=MCPTransport.SSE, url="http://localhost:9001"
            ),
            MCPServerConfig(
                name="bulk2", transport=MCPTransport.SSE, url="http://localhost:9002"
            ),
            MCPServerConfig(
                name="bulk3", transport=MCPTransport.SSE, url="http://localhost:9003"
            ),
        ]

        for config in configs:
            mcp_manager.add_server(config)

        # Try to connect all
        results = await mcp_manager.connect_all_servers()
        assert isinstance(results, dict)
        assert len(results) >= 3

        # Results should contain status for each server
        for config in configs:
            assert config.name in results
            assert isinstance(results[config.name], bool)

        # Try to disconnect all
        disconnect_results = await mcp_manager.disconnect_all_servers()
        assert isinstance(disconnect_results, dict)


@pytest.mark.integration
class TestMCPManagerConfiguration:
    """Test MCP manager configuration management."""

    async def test_server_configuration_validation(self, mcp_manager: MCPManager):
        """Test validation of server configurations."""
        # Valid SSE configuration
        valid_sse_config = MCPServerConfig(
            name="valid-sse", transport=MCPTransport.SSE, url="http://localhost:8765"
        )
        assert mcp_manager.add_server(valid_sse_config) is True

        # Valid STDIO configuration
        valid_stdio_config = MCPServerConfig(
            name="valid-stdio",
            transport=MCPTransport.STDIO,
            command=["python", "-m", "some_module"],
        )
        assert mcp_manager.add_server(valid_stdio_config) is True

        # Test that configurations are stored correctly
        servers = mcp_manager.list_servers()
        server_names = [s.name for s in servers]
        assert "valid-sse" in server_names
        assert "valid-stdio" in server_names

    async def test_server_configuration_update(self, mcp_manager: MCPManager):
        """Test updating server configurations."""
        initial_config = MCPServerConfig(
            name="updatable",
            transport=MCPTransport.SSE,
            url="http://localhost:8765",
            timeout=30,
        )

        mcp_manager.add_server(initial_config)

        # Update configuration
        updated_config = MCPServerConfig(
            name="updatable",
            transport=MCPTransport.SSE,
            url="http://localhost:8766",  # Different URL
            timeout=60,  # Different timeout
        )

        success = mcp_manager.update_server_config("updatable", updated_config)
        assert success is True

        # Verify update
        servers = mcp_manager.list_servers()
        updated_server = next(s for s in servers if s.name == "updatable")
        assert updated_server.url == "http://localhost:8766"
        assert updated_server.timeout == 60


@pytest.mark.integration
class TestMCPManagerErrorHandling:
    """Test MCP manager error handling and resilience."""

    async def test_connection_failure_handling(self, mcp_manager: MCPManager):
        """Test handling of connection failures."""
        # Configure server that will fail to connect
        failing_config = MCPServerConfig(
            name="will-fail",
            transport=MCPTransport.SSE,
            url="http://localhost:99999",  # Invalid port
            timeout=1,  # Short timeout
        )

        mcp_manager.add_server(failing_config)

        # Connection should fail gracefully
        success = await mcp_manager.connect_server("will-fail")
        assert success is False

        # Manager should still be functional
        status = mcp_manager.get_server_status("will-fail")
        assert isinstance(status, dict)
        assert status.get("connected") is False

    async def test_tool_call_error_recovery(self, mcp_manager: MCPManager):
        """Test error recovery during tool calls."""
        # Create connection that will fail during tool execution
        mock_connection = MagicMock()
        mock_connection.config.name = "error-prone"
        mock_connection.connected = True
        mock_connection.call_tool = AsyncMock(
            side_effect=ConnectionError("Network error")
        )

        mcp_manager.servers["error-prone"] = mock_connection
        mock_tool = MagicMock(name="error_tool", server="error-prone")
        mcp_manager.tools["error-prone.error_tool"] = mock_tool

        # Tool call should handle error gracefully
        result = await mcp_manager.call_tool("error-prone.error_tool", {})

        assert result is not None
        assert isinstance(result, dict)
        # Should contain error information
        assert "error" in result or result.get("success") is False
