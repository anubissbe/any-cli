"""
LSP Manager for embedded Language Server Protocol support.

This module provides a simplified interface to the solidlsp library from Serena,
enabling direct code analysis capabilities within Plato without external processes.
"""

import asyncio
import logging
import os
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import fallback analyzer
from .fallback_analyzer import FallbackUniversalAnalyzer

# Import core solidlsp components
try:
    # Add serena to path if not already available
    serena_path = "/opt/serena-repo/src"
    if serena_path not in sys.path:
        sys.path.insert(0, serena_path)

    from solidlsp.ls import SolidLanguageServer
    from solidlsp.ls_config import Language, LanguageServerConfig
    from solidlsp.ls_logger import LanguageServerLogger
    from solidlsp.ls_types import (
        UnifiedSymbolInformation,
        Location,
        Position,
        Range,
        SymbolKind,
        Diagnostic,
        Hover,
        CompletionItem,
    )
    from solidlsp.settings import SolidLSPSettings

    SOLIDLSP_AVAILABLE = True
except ImportError as e:
    SOLIDLSP_AVAILABLE = False
    # Use DEBUG level since fallback analyzer works perfectly
    logging.debug(f"solidlsp not available (using fallback analyzer): {e}")
    # Define minimal types for fallback
    UnifiedSymbolInformation = Dict[str, Any]
    Location = Dict[str, Any]
    Position = Dict[str, Any]
    Range = Dict[str, Any]
    SymbolKind = int
    Diagnostic = Dict[str, Any]
    Hover = Dict[str, Any]
    CompletionItem = Dict[str, Any]

logger = logging.getLogger(__name__)


class LSPManager:
    """
    Manages embedded LSP functionality for code analysis.

    Provides a simplified interface to language server operations like:
    - Symbol navigation (get symbols, find references, find definitions)
    - Code diagnostics (syntax errors, type errors)
    - Code completion and hover information
    """

    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize the LSP Manager.

        Args:
            workspace_root: Root directory for the workspace. Defaults to current directory.
        """
        self.workspace_root = workspace_root or os.getcwd()
        self.language_servers: Dict[str, SolidLanguageServer] = {}
        self.logger = self._setup_logger()
        self._lock = threading.Lock()

        # Check if solidlsp is available
        if not SOLIDLSP_AVAILABLE:
            logger.debug(
                "solidlsp library not available - using universal fallback analyzer (supports all languages)"
            )

        # Default configuration
        self.solidlsp_settings = self._create_settings() if SOLIDLSP_AVAILABLE else None
        self.fallback_analyzer = FallbackUniversalAnalyzer()

    def _setup_logger(self):
        """Set up logging for language server operations."""
        if SOLIDLSP_AVAILABLE:
            # Create a logger compatible with solidlsp
            return LanguageServerLogger(logger_name="plato_lsp")
        else:
            # Return a mock logger
            class MockLogger:
                def log(self, message, level=logging.INFO):
                    logger.log(level, message)

            return MockLogger()

    def _create_settings(self):
        """Create solidlsp settings."""
        # Create a temporary directory for LSP resources
        ls_resources_dir = os.path.join(tempfile.gettempdir(), "plato_lsp_resources")
        os.makedirs(ls_resources_dir, exist_ok=True)

        return SolidLSPSettings(
            ls_resources_dir=ls_resources_dir,
            trace_lsp_communication=False,
        )

    def get_or_create_language_server(self, file_path: str, language: str = "python"):
        """
        Get or create a language server for the given file.

        Args:
            file_path: Path to the file to analyze
            language: Programming language (default: python)

        Returns:
            Language server instance or None if not available
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("solidlsp not available - fallback analyzer will be used")
            return None

        # Determine workspace root (look for common project indicators)
        workspace_root = self._find_workspace_root(file_path)
        server_key = f"{language}:{workspace_root}"

        with self._lock:
            if server_key in self.language_servers:
                return self.language_servers[server_key]

            try:
                # Create language server configuration
                config = LanguageServerConfig(
                    code_language=(
                        Language.PYTHON if language == "python" else Language.PYTHON
                    ),
                    ignored_paths=[
                        ".git/**",
                        "__pycache__/**",
                        "*.pyc",
                        ".venv/**",
                        "venv/**",
                        "node_modules/**",
                        ".env/**",
                        "build/**",
                        "dist/**",
                    ],
                    trace_lsp_communication=False,
                    start_independent_lsp_process=False,
                )

                # Create language server
                ls = SolidLanguageServer.create(
                    config=config,
                    logger=self.logger,
                    repository_root_path=workspace_root,
                    solidlsp_settings=self.solidlsp_settings,
                )

                # Start the server
                ls.start()

                self.language_servers[server_key] = ls
                logger.info(
                    f"Created language server for {language} in {workspace_root}"
                )
                return ls

            except Exception as e:
                logger.error(f"Failed to create language server: {e}")
                return None

    def _find_workspace_root(self, file_path: str) -> str:
        """
        Find the workspace root by looking for project indicators.

        Args:
            file_path: Path to start searching from

        Returns:
            Workspace root path
        """
        current_path = (
            Path(file_path).parent if os.path.isfile(file_path) else Path(file_path)
        )

        # Look for common project indicators
        indicators = [
            ".git",
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "package.json",
            "Cargo.toml",
            ".project",
            "go.mod",
        ]

        while current_path != current_path.parent:
            for indicator in indicators:
                if (current_path / indicator).exists():
                    return str(current_path)
            current_path = current_path.parent

        # Fallback to the directory containing the file
        return str(Path(file_path).parent if os.path.isfile(file_path) else file_path)

    def _get_symbol_at_position(
        self, file_path: str, line: int, column: int
    ) -> Optional[str]:
        """
        Extract the symbol name at a specific position in a file.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)

        Returns:
            Symbol name at the position or None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if 0 <= line < len(lines):
                line_text = lines[line]

                # Simple extraction: find word boundaries around the column
                if 0 <= column < len(line_text):
                    # Find the start of the identifier
                    start = column
                    while start > 0 and (
                        line_text[start - 1].isalnum() or line_text[start - 1] == "_"
                    ):
                        start -= 1

                    # Find the end of the identifier
                    end = column
                    while end < len(line_text) and (
                        line_text[end].isalnum() or line_text[end] == "_"
                    ):
                        end += 1

                    if start < end:
                        symbol_name = line_text[start:end]
                        if symbol_name and (
                            symbol_name[0].isalpha() or symbol_name[0] == "_"
                        ):
                            return symbol_name

            return None

        except Exception as e:
            logger.error(
                f"Failed to extract symbol at {file_path}:{line}:{column}: {e}"
            )
            return None

    async def get_symbols(
        self, file_path: str, include_body: bool = False, language: str = "python"
    ):
        """
        Get symbols from a file.

        Args:
            file_path: Path to the file to analyze
            include_body: Whether to include symbol bodies in results
            language: Programming language

        Returns:
            List of symbols found in the file
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback universal symbol analyzer")
            return self.fallback_analyzer.get_symbols(
                file_path=file_path, include_body=include_body, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return []

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Get document symbols
            symbols, root_symbols = ls.request_document_symbols(
                rel_path, include_body=include_body
            )
            return symbols

        except Exception as e:
            logger.error(f"Failed to get symbols from {file_path}: {e}")
            return []

    async def find_references(
        self, file_path: str, line: int, column: int, language: str = "python"
    ):
        """
        Find references to a symbol at the given position.

        Args:
            file_path: Path to the file containing the symbol
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            List of reference locations
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback reference search")
            return self.fallback_analyzer.find_references(
                file_path=file_path, line=line, column=column, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return []

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Find references
            references = ls.request_references(rel_path, line, column)
            return references

        except Exception as e:
            logger.error(
                f"Failed to find references in {file_path}:{line}:{column}: {e}"
            )
            return []

    async def find_definition(
        self, file_path: str, line: int, column: int, language: str = "python"
    ):
        """
        Find definition of a symbol at the given position.

        Args:
            file_path: Path to the file containing the symbol
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            List of definition locations
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback definition finder")
            return self.fallback_analyzer.find_definition(
                file_path=file_path, line=line, column=column, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return []

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Find definition
            definitions = ls.request_definition(rel_path, line, column)
            return definitions

        except Exception as e:
            logger.error(
                f"Failed to find definition in {file_path}:{line}:{column}: {e}"
            )
            return []

    async def get_diagnostics(self, file_path: str, language: str = "python"):
        """
        Get diagnostics (errors, warnings) for a file.

        Args:
            file_path: Path to the file to analyze
            language: Programming language

        Returns:
            List of diagnostics
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback diagnostics analyzer")
            return self.fallback_analyzer.get_diagnostics(
                file_path=file_path, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return []

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Get diagnostics
            diagnostics = ls.request_text_document_diagnostics(rel_path)
            return diagnostics

        except Exception as e:
            logger.error(f"Failed to get diagnostics for {file_path}: {e}")
            return []

    async def get_hover_info(
        self, file_path: str, line: int, column: int, language: str = "python"
    ):
        """
        Get hover information for a symbol at the given position.

        Args:
            file_path: Path to the file containing the symbol
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            Hover information or None
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback hover info")
            return self.fallback_analyzer.get_hover_info(
                file_path=file_path, line=line, column=column, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return None

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Get hover info
            hover = ls.request_hover(rel_path, line, column)
            return hover

        except Exception as e:
            logger.error(
                f"Failed to get hover info for {file_path}:{line}:{column}: {e}"
            )
            return None

    async def get_completions(
        self, file_path: str, line: int, column: int, language: str = "python"
    ):
        """
        Get code completions at the given position.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            List of completion items
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback completions")
            return self.fallback_analyzer.get_completions(
                file_path=file_path, line=line, column=column, language=language
            )

        ls = self.get_or_create_language_server(file_path, language)
        if not ls:
            return []

        try:
            # Convert to relative path
            workspace_root = self._find_workspace_root(file_path)
            rel_path = os.path.relpath(file_path, workspace_root)

            # Get completions
            completions = ls.request_completions(rel_path, line, column)
            return completions

        except Exception as e:
            logger.error(
                f"Failed to get completions for {file_path}:{line}:{column}: {e}"
            )
            return []

    async def workspace_symbols(self, query: str, workspace_root: str = None):
        """
        Search for symbols across the workspace.

        Args:
            query: Search query
            workspace_root: Root directory to search in

        Returns:
            List of matching symbols
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback workspace symbols")
            return self.fallback_analyzer.workspace_symbols(
                query=query, workspace_root=workspace_root
            )

        # TODO: Implement solidlsp version
        return []

    async def call_hierarchy(
        self, file_path: str, line: int, column: int, language: str = "python"
    ):
        """
        Get call hierarchy for a function at the given position.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            Call hierarchy information
        """
        if not SOLIDLSP_AVAILABLE:
            logger.debug("Using fallback call hierarchy")
            return self.fallback_analyzer.call_hierarchy(
                file_path=file_path, line=line, column=column, language=language
            )

        # TODO: Implement solidlsp version
        return {}

    def cleanup(self):
        """Clean up language servers."""
        with self._lock:
            for ls in self.language_servers.values():
                try:
                    ls.stop()
                except Exception as e:
                    logger.error(f"Error stopping language server: {e}")
            self.language_servers.clear()

    def __del__(self):
        """Clean up on destruction."""
        self.cleanup()
