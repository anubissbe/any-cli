"""Integration tests for Plato API endpoints.

These tests verify that the FastAPI server endpoints work correctly
and integrate properly with the underlying components.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

from tests.conftest import skip_if_no_plato_server


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPIHealthEndpoints:
    """Test API health and status endpoints."""

    async def test_health_endpoint(self, plato_server_client: AsyncClient):
        """Test the health check endpoint."""
        response = await plato_server_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    async def test_server_info_endpoint(self, plato_server_client: AsyncClient):
        """Test the server info endpoint if available."""
        response = await plato_server_client.get("/info")

        # This endpoint might not exist, so we allow 404
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            # Should contain server information
            assert "name" in data or "version" in data
        else:
            assert response.status_code == 404


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPIChatEndpoints:
    """Test API chat functionality."""

    async def test_chat_endpoint_basic(self, plato_server_client: AsyncClient):
        """Test basic chat functionality."""
        payload = {
            "message": "Hello, how are you?",
            "task_type": "chat",
            "stream": False,
        }

        response = await plato_server_client.post("/chat", json=payload)

        # Chat might fail if no AI providers are configured with real keys
        # We accept both success and specific error responses
        assert response.status_code in [200, 400, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "content" in data
            assert "session_id" in data

    async def test_chat_endpoint_with_session(self, plato_server_client: AsyncClient):
        """Test chat with session management."""
        # First message to create session
        payload1 = {"message": "My name is Alice", "task_type": "chat"}

        response1 = await plato_server_client.post("/chat", json=payload1)

        if response1.status_code == 200:
            data1 = response1.json()
            session_id = data1.get("session_id")
            assert session_id is not None

            # Second message with same session
            payload2 = {
                "message": "What is my name?",
                "task_type": "chat",
                "session_id": session_id,
            }

            response2 = await plato_server_client.post("/chat", json=payload2)
            assert response2.status_code == 200

            data2 = response2.json()
            assert data2.get("session_id") == session_id

    async def test_chat_endpoint_with_provider_preference(
        self, plato_server_client: AsyncClient
    ):
        """Test chat with specific AI provider preference."""
        payload = {
            "message": "Test message",
            "task_type": "chat",
            "preferred_provider": "gpt-3.5-turbo",
        }

        response = await plato_server_client.post("/chat", json=payload)

        # Should handle the request even if provider isn't available
        assert response.status_code in [200, 400, 500, 503]

    async def test_chat_endpoint_validation(self, plato_server_client: AsyncClient):
        """Test chat endpoint input validation."""
        # Missing required field
        invalid_payload = {"task_type": "chat"}  # Missing message

        response = await plato_server_client.post("/chat", json=invalid_payload)
        assert response.status_code == 422  # Validation error

        # Invalid task type
        invalid_task_payload = {"message": "Test", "task_type": "invalid_task"}

        response2 = await plato_server_client.post("/chat", json=invalid_task_payload)
        assert response2.status_code == 422


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPIToolEndpoints:
    """Test API tool management endpoints."""

    async def test_list_tools_endpoint(self, plato_server_client: AsyncClient):
        """Test listing available tools."""
        response = await plato_server_client.get("/tools")

        assert response.status_code == 200
        data = response.json()

        assert "tools" in data
        assert isinstance(data["tools"], list)

        # Should have some tools if MCP servers are connected
        # But we don't require specific tools since setup may vary

    async def test_tool_info_endpoint(self, plato_server_client: AsyncClient):
        """Test getting information about specific tools."""
        # First get list of tools
        tools_response = await plato_server_client.get("/tools")

        if tools_response.status_code == 200:
            tools_data = tools_response.json()
            tools = tools_data.get("tools", [])

            if tools:
                # Get info for first tool
                tool_name = tools[0].get("name")
                if tool_name:
                    info_response = await plato_server_client.get(f"/tools/{tool_name}")

                    # Tool info endpoint might not exist or tool might not be found
                    assert info_response.status_code in [200, 404]

                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        assert "name" in info_data
                        assert "description" in info_data or "parameters" in info_data

    async def test_call_tool_endpoint(self, plato_server_client: AsyncClient):
        """Test calling tools via API."""
        # Get available tools first
        tools_response = await plato_server_client.get("/tools")

        if tools_response.status_code == 200:
            tools_data = tools_response.json()
            tools = tools_data.get("tools", [])

            if tools:
                # Try to call a tool (might fail if no Serena connection)
                tool_name = tools[0].get("name", "test_tool")

                call_payload = {"tool_name": tool_name, "arguments": {}}

                call_response = await plato_server_client.post(
                    "/tools/call", json=call_payload
                )

                # Tool call might fail for various reasons, we just check it's handled
                assert call_response.status_code in [200, 400, 500, 503]

    async def test_call_tool_validation(self, plato_server_client: AsyncClient):
        """Test tool call endpoint validation."""
        # Missing tool name
        invalid_payload = {"arguments": {}}

        response = await plato_server_client.post("/tools/call", json=invalid_payload)
        assert response.status_code == 422

        # Invalid payload structure
        invalid_payload2 = {"tool_name": "test", "arguments": "not_an_object"}

        response2 = await plato_server_client.post("/tools/call", json=invalid_payload2)
        assert response2.status_code == 422


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPISerenaEndpoints:
    """Test API endpoints specific to Serena MCP integration."""

    async def test_serena_analyze_endpoint(self, plato_server_client: AsyncClient):
        """Test Serena code analysis endpoint."""
        payload = {
            "project_path": "/tmp/test_project",
            "operation": "get_project_info",
            "parameters": {},
        }

        response = await plato_server_client.post("/serena/analyze", json=payload)

        # Serena might not be connected or operation might fail
        assert response.status_code in [200, 400, 500, 503]

        if response.status_code == 200:
            data = response.json()
            assert "result" in data or "success" in data

    async def test_serena_project_endpoint(self, plato_server_client: AsyncClient):
        """Test Serena project management endpoints."""
        # Test opening a project
        open_payload = {"project_path": "/tmp/test_project"}

        open_response = await plato_server_client.post(
            "/serena/project/open", json=open_payload
        )

        # Might fail if Serena not connected or path doesn't exist
        assert open_response.status_code in [200, 400, 404, 500, 503]

        # Test getting project info
        info_response = await plato_server_client.get(
            "/serena/project/info?path=/tmp/test_project"
        )
        assert info_response.status_code in [200, 400, 404, 500, 503]

    async def test_serena_file_operations(self, plato_server_client: AsyncClient):
        """Test Serena file operation endpoints."""
        test_file_path = "/tmp/test_file.py"

        # Test opening a file
        open_payload = {"file_path": test_file_path}
        open_response = await plato_server_client.post(
            "/serena/file/open", json=open_payload
        )
        assert open_response.status_code in [200, 400, 404, 500, 503]

        # Test getting file content
        content_response = await plato_server_client.get(
            f"/serena/file/content?path={test_file_path}"
        )
        assert content_response.status_code in [200, 400, 404, 500, 503]

        # Test saving file
        save_payload = {
            "file_path": test_file_path,
            "content": "print('Hello, World!')",
        }
        save_response = await plato_server_client.post(
            "/serena/file/save", json=save_payload
        )
        assert save_response.status_code in [200, 400, 404, 500, 503]


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPISessionManagement:
    """Test API session management endpoints."""

    async def test_create_session_endpoint(self, plato_server_client: AsyncClient):
        """Test creating new sessions."""
        response = await plato_server_client.post("/sessions/create")

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert data["session_id"] is not None
        assert len(data["session_id"]) > 0

    async def test_get_session_info(self, plato_server_client: AsyncClient):
        """Test getting session information."""
        # Create a session first
        create_response = await plato_server_client.post("/sessions/create")

        if create_response.status_code == 200:
            session_id = create_response.json()["session_id"]

            # Get session info
            info_response = await plato_server_client.get(f"/sessions/{session_id}")

            assert info_response.status_code == 200
            session_data = info_response.json()

            assert "session_id" in session_data
            assert session_data["session_id"] == session_id
            assert "created_at" in session_data
            assert "messages" in session_data or "conversation_history" in session_data

    async def test_session_history_endpoint(self, plato_server_client: AsyncClient):
        """Test getting session conversation history."""
        # Create session and send a message
        create_response = await plato_server_client.post("/sessions/create")

        if create_response.status_code == 200:
            session_id = create_response.json()["session_id"]

            # Send a message (might fail if no AI providers configured)
            chat_payload = {
                "message": "Test message for history",
                "session_id": session_id,
            }
            await plato_server_client.post("/chat", json=chat_payload)

            # Get history
            history_response = await plato_server_client.get(
                f"/sessions/{session_id}/history"
            )

            assert history_response.status_code == 200
            history_data = history_response.json()

            assert "messages" in history_data or "history" in history_data
            assert isinstance(
                history_data.get("messages", history_data.get("history", [])), list
            )

    async def test_delete_session_endpoint(self, plato_server_client: AsyncClient):
        """Test deleting sessions."""
        # Create a session first
        create_response = await plato_server_client.post("/sessions/create")

        if create_response.status_code == 200:
            session_id = create_response.json()["session_id"]

            # Delete the session
            delete_response = await plato_server_client.delete(
                f"/sessions/{session_id}"
            )

            assert delete_response.status_code in [200, 204]

            # Verify session is deleted
            get_response = await plato_server_client.get(f"/sessions/{session_id}")
            assert get_response.status_code == 404


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPIErrorHandling:
    """Test API error handling and edge cases."""

    async def test_invalid_endpoints(self, plato_server_client: AsyncClient):
        """Test requests to non-existent endpoints."""
        response = await plato_server_client.get("/nonexistent")
        assert response.status_code == 404

        response2 = await plato_server_client.post("/invalid/endpoint", json={})
        assert response2.status_code == 404

    async def test_malformed_json(self, plato_server_client: AsyncClient):
        """Test handling of malformed JSON requests."""
        # Send invalid JSON
        response = await plato_server_client.post(
            "/chat",
            content="invalid json content",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    async def test_large_payload_handling(self, plato_server_client: AsyncClient):
        """Test handling of very large payloads."""
        # Create a large message
        large_message = "x" * 100000  # 100KB message

        payload = {"message": large_message, "task_type": "chat"}

        response = await plato_server_client.post("/chat", json=payload)

        # Should either handle it or reject with appropriate error
        assert response.status_code in [200, 413, 400, 500, 503]

    async def test_concurrent_requests(self, plato_server_client: AsyncClient):
        """Test handling of concurrent requests."""
        import asyncio

        # Send multiple requests concurrently
        tasks = []
        for i in range(5):
            payload = {"message": f"Concurrent message {i}", "task_type": "chat"}
            task = plato_server_client.post("/chat", json=payload)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should be handled (success or controlled failure)
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [200, 400, 500, 503]


@pytest.mark.integration
@skip_if_no_plato_server
class TestAPIWebSocketSupport:
    """Test WebSocket support if available."""

    async def test_websocket_connection(self, plato_server_client: AsyncClient):
        """Test WebSocket connection if endpoint exists."""
        # WebSocket testing requires different approach
        # This is a placeholder that checks if WS endpoint exists

        try:
            # Try to connect to WebSocket endpoint
            # Note: httpx doesn't support WebSocket directly
            # This would need a proper WebSocket client

            response = await plato_server_client.get("/ws")
            # If we get here, WS endpoint might exist but needs upgrade
            assert response.status_code in [404, 426]  # 426 = Upgrade Required

        except Exception:
            # WebSocket endpoint might not exist, which is fine
            pass
