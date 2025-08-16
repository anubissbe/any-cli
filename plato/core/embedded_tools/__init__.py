"""Embedded tools for Plato - Claude Code-like file operations."""

from .base import EmbeddedTool, ToolResult, ToolParameter, ToolError
from .file_tools import (
    ReadFileTool,
    WriteFileTool,
    EditFileTool,
    ListDirectoryTool,
    SearchFilesTool,
    CreateDirectoryTool,
)
from .tool_manager import ToolManager

__all__ = [
    # Base classes
    "EmbeddedTool",
    "ToolResult",
    "ToolParameter",
    "ToolError",
    # File tools
    "ReadFileTool",
    "WriteFileTool",
    "EditFileTool",
    "ListDirectoryTool",
    "SearchFilesTool",
    "CreateDirectoryTool",
    # Manager
    "ToolManager",
]
