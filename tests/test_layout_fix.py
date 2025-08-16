"""Tests for Layout object error fix in interactive CLI."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from plato.interactive_cli import (
    PlatoInteractiveCLI,
    ProjectContext,
    FileExplorer,
    SessionManager,
)


class TestLayoutFix:
    """Test the Layout object initialization fix."""

    @pytest.fixture
    def mock_console(self):
        """Mock console for testing."""
        with patch("plato.interactive_cli.Console") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_layout(self):
        """Mock Layout for testing."""
        with patch("plato.interactive_cli.Layout") as mock:
            layout_instance = MagicMock()
            layout_instance.__getitem__ = MagicMock()
            layout_instance.split_column = MagicMock()
            layout_instance.split_row = MagicMock()
            mock.return_value = layout_instance
            yield layout_instance

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx client."""
        with patch("plato.interactive_cli.httpx.AsyncClient") as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    def test_layout_initialization(self, mock_console, mock_layout, mock_httpx_client):
        """Test that Layout is properly initialized without errors."""
        # Create CLI instance
        cli = PlatoInteractiveCLI("http://localhost:8080")

        # Verify layout was created
        assert cli.layout is not None

        # Verify layout setup was called
        mock_layout.split_column.assert_called_once()

        # Get the main layout and verify row split
        main_layout = mock_layout.__getitem__.return_value
        main_layout.split_row.assert_called_once()

    def test_layout_update_without_errors(
        self, mock_console, mock_layout, mock_httpx_client
    ):
        """Test that layout updates don't cause errors."""
        cli = PlatoInteractiveCLI("http://localhost:8080")

        # Mock session manager
        cli.session_manager = MagicMock()
        cli.session_manager.get_context_summary.return_value = "Test session"

        # Test header update
        cli._update_header()

        # Verify no exceptions were raised and layout was accessed
        mock_layout.__getitem__.assert_called()

    @pytest.mark.asyncio
    async def test_full_startup_sequence(
        self, mock_console, mock_layout, mock_httpx_client
    ):
        """Test that the full startup sequence works without Layout errors."""
        cli = PlatoInteractiveCLI("http://localhost:8080")

        # Mock all the async methods to avoid actual network calls
        cli._show_welcome = AsyncMock()
        cli._check_server_connection = AsyncMock()
        cli._initialize_serena = AsyncMock()
        cli._detect_and_show_project = AsyncMock()
        cli._main_loop = AsyncMock()
        cli._cleanup = AsyncMock()

        # Mock running flag to exit immediately
        cli.running = False

        # This should not raise any Layout-related errors
        await cli.start()

        # Verify initialization methods were called
        cli._show_welcome.assert_called_once()
        cli._check_server_connection.assert_called_once()
        cli._initialize_serena.assert_called_once()
        cli._detect_and_show_project.assert_called_once()


class TestProjectContext:
    """Test ProjectContext functionality."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure."""
        # Create Python project structure
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "requirements.txt").write_text("pytest\nrequests")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "utils.py").write_text("def helper(): pass")
        return tmp_path

    def test_project_detection_python(self, temp_project):
        """Test Python project detection."""
        context = ProjectContext(str(temp_project))

        assert context.project_type == "python"
        assert context.language == "python"
        assert "requirements.txt" in context.config_files

    def test_project_summary(self, temp_project):
        """Test project summary generation."""
        context = ProjectContext(str(temp_project))
        summary = context.get_summary()

        assert summary["type"] == "python"
        assert summary["language"] == "python"
        assert summary["name"] == temp_project.name
        assert summary["path"] == str(temp_project)
        assert "requirements.txt" in summary["config_files"]

    def test_project_with_git(self, temp_project):
        """Test project with git repository."""
        # Create git repo
        import subprocess

        subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_project)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=temp_project
        )

        context = ProjectContext(str(temp_project))
        summary = context.get_summary()

        if summary.get("git"):
            assert "branch" in summary["git"] or "error" in summary["git"]


class TestFileExplorer:
    """Test FileExplorer functionality."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace."""
        # Create directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main file")
        (tmp_path / "src" / "utils.py").write_text("# utils")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("# tests")
        (tmp_path / "README.md").write_text("# Project")
        return tmp_path

    def test_file_tree_building(self, temp_workspace):
        """Test file tree construction."""
        explorer = FileExplorer(str(temp_workspace))
        tree = explorer.build_tree(max_depth=3)

        assert tree is not None
        # Tree should contain the root directory name
        assert temp_workspace.name in str(tree)

    def test_file_icon_assignment(self, temp_workspace):
        """Test file icon assignment."""
        explorer = FileExplorer(str(temp_workspace))

        # Test Python file icon
        py_file = temp_workspace / "test.py"
        icon = explorer._get_file_icon(py_file)
        assert icon == "🐍"

        # Test Markdown file icon
        md_file = temp_workspace / "README.md"
        icon = explorer._get_file_icon(md_file)
        assert icon == "📝"

    def test_file_color_assignment(self, temp_workspace):
        """Test file color assignment."""
        explorer = FileExplorer(str(temp_workspace))

        # Test Python file color
        py_file = temp_workspace / "test.py"
        color = explorer._get_file_color(py_file)
        assert color == "bright_yellow"

        # Test default color
        txt_file = temp_workspace / "unknown.xyz"
        color = explorer._get_file_color(txt_file)
        assert color == "white"


class TestSessionManager:
    """Test SessionManager functionality."""

    def test_session_initialization(self):
        """Test session manager initialization."""
        manager = SessionManager()

        assert manager.session_id is None
        assert manager.messages == []
        assert manager.context == {}
        assert manager.tokens_used == 0
        assert manager.current_provider is None

    def test_add_message(self):
        """Test adding messages to session."""
        manager = SessionManager()

        manager.add_message("user", "Hello", {"test": "metadata"})

        assert len(manager.messages) == 1
        message = manager.messages[0]
        assert message["role"] == "user"
        assert message["content"] == "Hello"
        assert message["metadata"]["test"] == "metadata"
        assert "timestamp" in message

    def test_context_summary(self):
        """Test context summary generation."""
        manager = SessionManager()
        manager.session_id = "test-123"
        manager.tokens_used = 150
        manager.current_provider = "claude"
        manager.add_message("user", "test message")

        summary = manager.get_context_summary()

        assert "test-123" in summary
        assert "150" in summary
        assert "1" in summary  # message count
        assert "claude" in summary
