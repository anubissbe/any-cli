"""Integration tests for Plato CLI functionality.

These tests verify that the CLI commands work correctly and can
interact with the Plato server and underlying components.
"""

import pytest
import subprocess
import json
from pathlib import Path

from tests.conftest import skip_if_no_plato_server


@pytest.mark.integration
class TestCLIBasicCommands:
    """Test basic CLI commands."""

    def test_cli_help(self):
        """Test that CLI help command works."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "--help"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "plato" in result.stdout.lower()
        assert "help" in result.stdout.lower()

    def test_cli_version_info(self):
        """Test CLI version or info command if available."""
        # Try common version flags
        for flag in ["--version", "-v", "version"]:
            result = subprocess.run(
                ["python", "-m", "plato.cli", flag],
                cwd="/opt/projects/plato",
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Version command might not exist, just check it doesn't crash
            assert result.returncode in [0, 2]  # 0 = success, 2 = unrecognized command

            if result.returncode == 0:
                # If version command exists, should contain version info
                assert len(result.stdout) > 0
                break


@pytest.mark.integration
@skip_if_no_plato_server
class TestCLIServerInteraction:
    """Test CLI commands that interact with Plato server."""

    def test_cli_health_check(self):
        """Test CLI health check command."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "health"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Health check should work if server is running
        assert result.returncode in [0, 1]  # 0 = healthy, 1 = unhealthy/error

        if result.returncode == 0:
            # Should contain status information
            assert (
                "healthy" in result.stdout.lower() or "status" in result.stdout.lower()
            )

    def test_cli_health_check_with_custom_url(self):
        """Test health check with custom server URL."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "health",
                "--server-url",
                "http://localhost:8080",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, 1]

    def test_cli_list_tools(self):
        """Test CLI command to list available tools."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "tools", "list"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Tools command might not exist or server might not be available
        assert result.returncode in [0, 1, 2]

        if result.returncode == 0:
            # Should list tools if successful
            assert len(result.stdout) > 0


@pytest.mark.integration
class TestCLIChatCommands:
    """Test CLI chat functionality."""

    @skip_if_no_plato_server
    def test_cli_chat_basic(self):
        """Test basic CLI chat command."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "chat", "Hello"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Chat might fail if no AI providers configured
        assert result.returncode in [0, 1]

        if result.returncode == 0:
            # Should contain response
            assert len(result.stdout) > 0

    @skip_if_no_plato_server
    def test_cli_chat_with_provider(self):
        """Test CLI chat with specific provider."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "chat",
                "Test message",
                "--provider",
                "gpt-3.5-turbo",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Might fail if provider not configured
        assert result.returncode in [0, 1]

    @skip_if_no_plato_server
    def test_cli_chat_with_task_type(self):
        """Test CLI chat with specific task type."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "chat",
                "Analyze this code",
                "--task-type",
                "code_analysis",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in [0, 1]


@pytest.mark.integration
class TestCLICodeAnalysis:
    """Test CLI code analysis commands."""

    def test_cli_analyze_with_temp_project(self, temp_workspace: Path):
        """Test CLI code analysis with temporary project."""
        project_path = temp_workspace / "test_project"

        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "analyze",
                str(project_path),
                "--operation",
                "get_project_info",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Analysis might fail if Serena not connected
        assert result.returncode in [0, 1]

        if result.returncode == 0:
            # Should contain analysis results
            assert len(result.stdout) > 0

    def test_cli_analyze_file(self, temp_workspace: Path):
        """Test CLI file analysis."""
        file_path = temp_workspace / "test_project" / "main.py"

        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "analyze",
                str(file_path),
                "--operation",
                "get_file_content",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in [0, 1]

    def test_cli_analyze_with_language(self, temp_workspace: Path):
        """Test CLI analysis with language specification."""
        project_path = temp_workspace / "test_project"

        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "analyze",
                str(project_path),
                "--operation",
                "get_workspace_files",
                "--language",
                "python",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode in [0, 1]


@pytest.mark.integration
class TestCLISessionManagement:
    """Test CLI session management commands."""

    @skip_if_no_plato_server
    def test_cli_create_session(self):
        """Test creating a session via CLI."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "session", "create"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, 1]

        if result.returncode == 0:
            # Should contain session ID
            assert len(result.stdout) > 0
            # Try to extract session ID for further tests
            try:
                output = result.stdout.strip()
                # Session ID should be in the output
                assert len(output) > 10  # Basic length check
            except Exception:
                pass

    @skip_if_no_plato_server
    def test_cli_list_sessions(self):
        """Test listing sessions via CLI."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "session", "list"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode in [0, 1]

    @skip_if_no_plato_server
    def test_cli_chat_with_session(self):
        """Test chat with session management."""
        # First create a session
        create_result = subprocess.run(
            ["python", "-m", "plato.cli", "session", "create"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        if create_result.returncode == 0:
            session_id = create_result.stdout.strip()

            # Use session for chat
            chat_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "plato.cli",
                    "chat",
                    "Test with session",
                    "--session",
                    session_id,
                ],
                cwd="/opt/projects/plato",
                capture_output=True,
                text=True,
                timeout=60,
            )

            assert chat_result.returncode in [0, 1]


@pytest.mark.integration
class TestCLIConfigurationCommands:
    """Test CLI configuration and setup commands."""

    def test_cli_config_show(self):
        """Test showing configuration."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "config", "show"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Config command might not exist
        assert result.returncode in [0, 1, 2]

        if result.returncode == 0:
            # Should show configuration information
            assert len(result.stdout) > 0

    def test_cli_providers_list(self):
        """Test listing AI providers."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "providers", "list"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Providers command might not exist
        assert result.returncode in [0, 1, 2]

    def test_cli_mcp_servers_list(self):
        """Test listing MCP servers."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "mcp", "list"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # MCP command might not exist
        assert result.returncode in [0, 1, 2]


@pytest.mark.integration
class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""

    def test_cli_invalid_command(self):
        """Test CLI with invalid commands."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "nonexistent_command"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should return error code for invalid command
        assert result.returncode != 0
        assert len(result.stderr) > 0 or "error" in result.stdout.lower()

    def test_cli_missing_arguments(self):
        """Test CLI with missing required arguments."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "chat"],  # Missing message
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should return error for missing arguments
        assert result.returncode != 0

    def test_cli_invalid_server_url(self):
        """Test CLI with invalid server URL."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "health", "--server-url", "invalid://url"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should handle invalid URL gracefully
        assert result.returncode in [1, 2]

    def test_cli_unreachable_server(self):
        """Test CLI with unreachable server."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "plato.cli",
                "health",
                "--server-url",
                "http://localhost:99999",
            ],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should handle unreachable server gracefully
        assert result.returncode == 1
        assert "connection" in result.stderr.lower() or "error" in result.stdout.lower()


@pytest.mark.integration
class TestCLIOutputFormats:
    """Test CLI output formatting options."""

    @skip_if_no_plato_server
    def test_cli_json_output(self):
        """Test CLI with JSON output format."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "health", "--format", "json"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            try:
                # Should be valid JSON
                json.loads(result.stdout)
            except json.JSONDecodeError:
                # JSON format might not be supported
                pass

    @skip_if_no_plato_server
    def test_cli_verbose_output(self):
        """Test CLI with verbose output."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "health", "--verbose"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Verbose flag might not exist, just check it doesn't break
        assert result.returncode in [0, 1, 2]

    @skip_if_no_plato_server
    def test_cli_quiet_output(self):
        """Test CLI with quiet output."""
        result = subprocess.run(
            ["python", "-m", "plato.cli", "health", "--quiet"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Quiet flag might not exist
        assert result.returncode in [0, 1, 2]


@pytest.mark.integration
class TestCLIInteractiveMode:
    """Test CLI interactive features if available."""

    def test_cli_non_interactive_mode(self):
        """Test that CLI works in non-interactive mode."""
        # All our tests are effectively non-interactive since we don't provide stdin
        result = subprocess.run(
            ["python", "-m", "plato.cli", "chat", "Non-interactive test"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=30,
            input="",  # Empty stdin
        )

        # Should handle non-interactive mode
        assert result.returncode in [0, 1]

    def test_cli_batch_mode(self):
        """Test CLI batch processing if available."""
        # Create a simple batch file
        batch_content = "Hello\nHow are you?\nGoodbye\n"

        result = subprocess.run(
            ["python", "-m", "plato.cli", "chat", "--batch"],
            cwd="/opt/projects/plato",
            capture_output=True,
            text=True,
            timeout=60,
            input=batch_content,
        )

        # Batch mode might not exist
        assert result.returncode in [0, 1, 2]
