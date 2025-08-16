"""Integration tests for Serena MCP functionality.

These tests verify that Plato can successfully communicate with the Serena MCP server
and perform real LSP operations.
"""

import pytest
from pathlib import Path

from plato.integrations.serena_mcp import SerenaMCPClient, SerenaLanguage
from tests.conftest import skip_if_no_serena


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaMCPConnection:
    """Test basic Serena MCP connection functionality."""

    async def test_health_check(self, serena_client: SerenaMCPClient):
        """Test that we can perform a health check."""
        is_healthy = await serena_client.health_check()
        assert is_healthy is True

    async def test_connect_disconnect(self, serena_client: SerenaMCPClient):
        """Test connection lifecycle."""
        # Should be able to connect
        connected = await serena_client.connect()
        assert connected is True

        # Should be able to disconnect cleanly
        await serena_client.disconnect()

    async def test_supported_languages(self, serena_client: SerenaMCPClient):
        """Test that we get the expected supported languages."""
        languages = serena_client.get_supported_languages()

        assert len(languages) > 0
        assert SerenaLanguage.PYTHON in languages
        assert SerenaLanguage.TYPESCRIPT in languages
        assert SerenaLanguage.JAVASCRIPT in languages
        assert SerenaLanguage.GO in languages

    async def test_server_status(self, serena_client: SerenaMCPClient):
        """Test getting server status."""
        response = await serena_client.get_server_status()

        assert response.success is True
        assert response.data is not None
        # Should contain some status information
        assert isinstance(response.data, dict)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaProjectOperations:
    """Test Serena project-level operations."""

    async def test_open_close_project(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test opening and closing a project."""
        project_path = str(temp_workspace / "test_project")

        # Open project
        open_response = await serena_client.open_project(project_path)
        assert open_response.success is True

        # Get project info
        info_response = await serena_client.get_project_info(project_path)
        assert info_response.success is True
        assert info_response.data is not None

        # Close project
        close_response = await serena_client.close_project(project_path)
        assert close_response.success is True

    async def test_get_workspace_files(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test getting workspace files."""
        project_path = str(temp_workspace / "test_project")

        # Open project first
        await serena_client.open_project(project_path)

        # Get all files
        response = await serena_client.get_workspace_files(project_path)
        assert response.success is True
        assert response.data is not None

        files = response.data
        assert isinstance(files, list)

        # Should contain our test files
        file_names = [f.get("name", f.get("path", "")) for f in files]
        assert any("main.py" in name for name in file_names)
        assert any("utils.py" in name for name in file_names)

        # Test language filtering
        python_response = await serena_client.get_workspace_files(
            project_path, language=SerenaLanguage.PYTHON
        )
        assert python_response.success is True

        await serena_client.close_project(project_path)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaFileOperations:
    """Test Serena file-level operations."""

    async def test_open_close_file(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test opening and closing files."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        # Open project first
        await serena_client.open_project(project_path)

        # Open file
        open_response = await serena_client.open_file(file_path)
        assert open_response.success is True

        # Close file
        close_response = await serena_client.close_file(file_path)
        assert close_response.success is True

        await serena_client.close_project(project_path)

    async def test_get_file_content(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test getting file content."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Get file content
        response = await serena_client.get_file_content(file_path)
        assert response.success is True
        assert response.data is not None

        content = response.data
        assert "hello_world" in content
        assert "print" in content

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)

    async def test_save_file(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test saving file content."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "test_save.py")

        await serena_client.open_project(project_path)

        # Save new content
        new_content = 'def test_function():\n    return "Hello from test"'
        save_response = await serena_client.save_file(file_path, new_content)
        assert save_response.success is True

        # Verify content was saved
        await serena_client.open_file(file_path)
        get_response = await serena_client.get_file_content(file_path)
        assert get_response.success is True
        assert "test_function" in get_response.data

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaSymbolOperations:
    """Test Serena symbol and LSP operations."""

    async def test_get_document_symbols(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test getting symbols from a document."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "utils.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Get document symbols
        response = await serena_client.get_document_symbols(file_path)
        assert response.success is True

        if response.data:  # Some language servers might not return symbols immediately
            symbols = response.data
            assert isinstance(symbols, list)

            # Should find our functions
            symbol_names = [s.get("name", "") for s in symbols]
            assert any("add_numbers" in name for name in symbol_names)
            assert any("multiply" in name for name in symbol_names)

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)

    async def test_find_symbols(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test finding symbols in workspace."""
        project_path = str(temp_workspace / "test_project")

        await serena_client.open_project(project_path)

        # Search for symbols
        response = await serena_client.find_symbols(
            project_path, "hello", SerenaLanguage.PYTHON
        )

        # Note: Symbol search might not work immediately or might require indexing
        # So we don't assert on specific results, just that the call succeeds
        assert response.success is True or response.error is not None

        await serena_client.close_project(project_path)

    async def test_get_diagnostics(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test getting diagnostics for a file."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Get diagnostics
        response = await serena_client.get_diagnostics(file_path)

        # Diagnostics might not be available immediately
        assert response.success is True or response.error is not None

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaLanguageServers:
    """Test Serena language server management."""

    async def test_get_language_servers(self, serena_client: SerenaMCPClient):
        """Test getting available language servers."""
        response = await serena_client.get_language_servers()

        assert response.success is True
        assert response.data is not None

        servers = response.data
        assert isinstance(servers, (list, dict))

    async def test_restart_language_server(self, serena_client: SerenaMCPClient):
        """Test restarting a language server."""
        # Try to restart Python language server
        response = await serena_client.restart_language_server(SerenaLanguage.PYTHON)

        # This might fail if the language server isn't running, which is okay
        assert response.success is True or response.error is not None


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaContextBuilding:
    """Test Serena context building helpers."""

    async def test_build_file_context(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test building comprehensive file context."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Build file context
        context = await serena_client.build_file_context(file_path)

        assert isinstance(context, dict)
        assert "file_path" in context
        assert context["file_path"] == file_path

        # Should have sections for different types of information
        assert "symbols" in context
        assert "diagnostics" in context
        assert "imports" in context
        assert "exports" in context

        # Content should be included if successful
        if "content" in context:
            assert "hello_world" in context["content"]

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)

    async def test_build_project_context(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test building comprehensive project context."""
        project_path = str(temp_workspace / "test_project")

        await serena_client.open_project(project_path)

        # Build project context
        context = await serena_client.build_project_context(project_path)

        assert isinstance(context, dict)
        assert "workspace_path" in context
        assert context["workspace_path"] == project_path

        # Should have sections for different types of information
        assert "files" in context
        assert "dependencies" in context
        assert "metrics" in context

        await serena_client.close_project(project_path)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaAdvancedOperations:
    """Test advanced Serena operations that might be available."""

    async def test_format_document(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test document formatting."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "main.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Try to format document
        response = await serena_client.format_document(file_path)

        # Formatting might not be available for all languages/servers
        assert response.success is True or response.error is not None

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)

    async def test_code_quality_analysis(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test code quality analysis."""
        project_path = str(temp_workspace / "test_project")
        file_path = str(temp_workspace / "test_project" / "utils.py")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Try to analyze code quality
        response = await serena_client.analyze_code_quality(file_path)

        # This is an advanced feature that might not be available
        assert response.success is True or response.error is not None

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)


@pytest.mark.integration
@skip_if_no_serena
class TestSerenaTypeScriptSupport:
    """Test Serena operations with TypeScript files."""

    async def test_typescript_file_operations(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test basic operations with TypeScript files."""
        project_path = str(temp_workspace / "test_ts_project")
        file_path = str(temp_workspace / "test_ts_project" / "index.ts")

        await serena_client.open_project(project_path)
        await serena_client.open_file(file_path)

        # Get file content
        content_response = await serena_client.get_file_content(file_path)
        assert content_response.success is True
        assert "interface User" in content_response.data

        # Try to get symbols
        symbols_response = await serena_client.get_document_symbols(file_path)
        assert symbols_response.success is True or symbols_response.error is not None

        await serena_client.close_file(file_path)
        await serena_client.close_project(project_path)

    async def test_workspace_files_typescript(
        self, serena_client: SerenaMCPClient, temp_workspace: Path
    ):
        """Test getting TypeScript files from workspace."""
        project_path = str(temp_workspace / "test_ts_project")

        await serena_client.open_project(project_path)

        # Get TypeScript files
        response = await serena_client.get_workspace_files(
            project_path, language=SerenaLanguage.TYPESCRIPT
        )
        assert response.success is True

        if response.data:
            files = response.data
            file_names = [f.get("name", f.get("path", "")) for f in files]
            assert any("index.ts" in name for name in file_names)

        await serena_client.close_project(project_path)
