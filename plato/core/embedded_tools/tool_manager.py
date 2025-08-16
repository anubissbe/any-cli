"""Tool manager for embedded tools."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Type

from .base import EmbeddedTool, ToolError, ToolResult
from .file_tools import (
    CreateDirectoryTool,
    EditFileTool,
    ListDirectoryTool,
    ReadFileTool,
    SearchFilesTool,
    WriteFileTool,
)

logger = logging.getLogger(__name__)

# Import LSP tools (with fallback for missing dependencies)
try:
    from ..embedded_lsp import (
        GetSymbolsTool,
        FindReferencesTool,
        FindDefinitionTool,
        GetDiagnosticsTool,
        CodeAnalysisTool,
        HoverInfoTool,
        CompletionsTool,
    )

    LSP_TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LSP tools not available: {e}")
    LSP_TOOLS_AVAILABLE = False


class ToolManager:
    """Manages embedded tools for Plato."""

    def __init__(self):
        self.tools: Dict[str, EmbeddedTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default embedded tools."""
        default_tools = [
            ReadFileTool(),
            WriteFileTool(),
            EditFileTool(),
            ListDirectoryTool(),
            SearchFilesTool(),
            CreateDirectoryTool(),
        ]

        # Add LSP tools if available
        if LSP_TOOLS_AVAILABLE:
            lsp_tools = [
                GetSymbolsTool(),
                FindReferencesTool(),
                FindDefinitionTool(),
                GetDiagnosticsTool(),
                CodeAnalysisTool(),
                HoverInfoTool(),
                CompletionsTool(),
            ]
            default_tools.extend(lsp_tools)
            logger.info("LSP tools registered successfully")
        else:
            logger.info("LSP tools not available - skipping registration")

        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: EmbeddedTool):
        """Register a tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def unregister_tool(self, tool_name: str):
        """Unregister a tool."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[EmbeddedTool]:
        """Get a tool by name."""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self.tools.keys())

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self.tools.values()]

    def get_openai_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas in OpenAI format."""
        openai_tools = []
        for tool in self.tools.values():
            schema = tool.get_schema()
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema["name"],
                        "description": schema["description"],
                        "parameters": schema["parameters"],
                    },
                }
            )
        return openai_tools

    def format_tools_for_ai(self) -> str:
        """Format all tools for AI understanding."""
        lines = ["Available Embedded Tools:", "=" * 40]

        for tool in self.tools.values():
            lines.append("")
            lines.append(tool.format_for_ai())
            lines.append("-" * 40)

        return "\n".join(lines)

    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ToolError(f"Tool not found: {tool_name}")

        try:
            logger.info(f"Executing tool: {tool_name} with params: {kwargs}")
            result = await tool.execute(**kwargs)
            logger.info(f"Tool {tool_name} completed successfully")
            return result
        except ToolError as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            return ToolResult(success=False, error=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in tool {tool_name}: {e}")
            return ToolResult(success=False, error=f"Unexpected error: {e}")

    def parse_tool_request(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a tool request from text (JSON or natural language)."""
        # Try to parse as JSON first
        try:
            if "{" in text and "}" in text:
                # Extract JSON from text
                start = text.index("{")
                end = text.rindex("}") + 1
                json_str = text[start:end]
                data = json.loads(json_str)

                if "tool" in data or "name" in data:
                    return {
                        "tool": data.get("tool") or data.get("name"),
                        "parameters": data.get("parameters", {}),
                    }
        except (json.JSONDecodeError, ValueError):
            pass

        # Try to parse natural language
        return self._parse_natural_language(text)

    def _parse_natural_language(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse natural language tool request."""
        text_lower = text.lower()

        # Read file patterns
        if any(
            phrase in text_lower
            for phrase in ["read file", "show file", "open file", "cat "]
        ):
            # Extract file path
            import re

            # Try different patterns
            patterns = [
                r"(?:read|show|open|cat)\s+(?:file\s+)?['\"]?([^\s'\"]+)['\"]?",
                r"(?:the\s+)?file\s+['\"]?([^\s'\"]+)['\"]?",
            ]

            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    file_path = match.group(1)
                    return {
                        "tool": "ReadFileTool",
                        "parameters": {"file_path": file_path},
                    }

        # Write file patterns
        if any(
            phrase in text_lower for phrase in ["write file", "create file", "save to"]
        ):
            # This would need more sophisticated parsing for content
            # For now, return None to indicate manual handling needed
            return None

        # List directory patterns
        if any(
            phrase in text_lower
            for phrase in ["list dir", "ls ", "show dir", "list files"]
        ):
            import re

            # Extract directory path if specified
            match = re.search(
                r"(?:list|ls|show)\s+(?:dir|directory|files)?\s*['\"]?([^\s'\"]*)['\"]?",
                text_lower,
            )
            if match:
                dir_path = match.group(1) or "."
                return {
                    "tool": "ListDirectoryTool",
                    "parameters": {"directory_path": dir_path},
                }

        # Search patterns
        if any(phrase in text_lower for phrase in ["search for", "find ", "grep "]):
            import re

            # Extract search pattern
            match = re.search(
                r"(?:search for|find|grep)\s+['\"]?([^'\"]+)['\"]?", text_lower
            )
            if match:
                pattern = match.group(1)
                return {"tool": "SearchFilesTool", "parameters": {"pattern": pattern}}

        return None

    def format_tool_result(self, result: ToolResult) -> str:
        """Format tool result for display."""
        if result.success:
            lines = ["✅ Tool executed successfully"]

            if isinstance(result.data, str):
                lines.append("")
                lines.append(result.data)
            elif result.data is not None:
                lines.append("")
                lines.append(json.dumps(result.data, indent=2, default=str))

            if result.metadata:
                lines.append("")
                lines.append("Metadata:")
                for key, value in result.metadata.items():
                    lines.append(f"  {key}: {value}")
        else:
            lines = [f"❌ Tool execution failed: {result.error}"]

        return "\n".join(lines)

    async def execute_from_text(self, text: str) -> Optional[ToolResult]:
        """Execute a tool from text description."""
        request = self.parse_tool_request(text)
        if not request:
            return None

        tool_name = request["tool"]
        parameters = request.get("parameters", {})

        return await self.execute_tool(tool_name, **parameters)
