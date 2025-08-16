"""
Symbol operation tools using embedded LSP capabilities.

These tools provide symbol-based operations like getting symbols, finding references,
finding definitions, and getting diagnostics using the embedded LSP manager.
"""

import json
import os
from typing import List

from ..embedded_tools.base import (
    EmbeddedTool,
    ParameterType,
    ToolParameter,
    ToolResult,
    ToolError,
)
from .lsp_manager import LSPManager


class GetSymbolsTool(EmbeddedTool):
    """Get symbols from a Python file using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for getting symbols."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the Python file to analyze",
                required=True,
            ),
            ToolParameter(
                name="include_body",
                type=ParameterType.BOOLEAN,
                description="Whether to include symbol body/source code in results",
                required=False,
                default=False,
            ),
            ToolParameter(
                name="language",
                type=ParameterType.STRING,
                description="Programming language",
                required=False,
                default="python",
                enum=["python"],
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the get symbols operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            include_body = params.get("include_body", False)
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Get symbols using LSP
            symbols = await self.lsp_manager.get_symbols(
                file_path=file_path, include_body=include_body, language=language
            )

            # Format symbols for display
            formatted_symbols = []
            for symbol in symbols:
                symbol_info = {
                    "name": symbol.get("name", ""),
                    "kind": symbol.get("kind", 0),
                    "kind_name": self._get_symbol_kind_name(symbol.get("kind", 0)),
                    "range": symbol.get("range", {}),
                }

                if include_body and "body" in symbol:
                    symbol_info["body"] = symbol["body"]

                if "location" in symbol:
                    location = symbol["location"]
                    symbol_info["location"] = {
                        "file": location.get(
                            "relativePath", location.get("absolutePath", "")
                        ),
                        "line": location.get("range", {})
                        .get("start", {})
                        .get("line", 0),
                        "column": location.get("range", {})
                        .get("start", {})
                        .get("character", 0),
                    }

                formatted_symbols.append(symbol_info)

            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "symbol_count": len(formatted_symbols),
                    "symbols": formatted_symbols,
                },
                metadata={
                    "tool": "GetSymbolsTool",
                    "language": language,
                    "include_body": include_body,
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get symbols: {e}")

    def _get_symbol_kind_name(self, kind: int) -> str:
        """Get human-readable symbol kind name."""
        symbol_kinds = {
            1: "File",
            2: "Module",
            3: "Namespace",
            4: "Package",
            5: "Class",
            6: "Method",
            7: "Property",
            8: "Field",
            9: "Constructor",
            10: "Enum",
            11: "Interface",
            12: "Function",
            13: "Variable",
            14: "Constant",
            15: "String",
            16: "Number",
            17: "Boolean",
            18: "Array",
            19: "Object",
            20: "Key",
            21: "Null",
            22: "EnumMember",
            23: "Struct",
            24: "Event",
            25: "Operator",
            26: "TypeParameter",
        }
        return symbol_kinds.get(kind, f"Unknown({kind})")


class FindReferencesTool(EmbeddedTool):
    """Find references to a symbol at a specific position using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for finding references."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file containing the symbol",
                required=True,
            ),
            ToolParameter(
                name="line",
                type=ParameterType.INTEGER,
                description="Line number (0-based) of the symbol",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="column",
                type=ParameterType.INTEGER,
                description="Column number (0-based) of the symbol",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="language",
                type=ParameterType.STRING,
                description="Programming language",
                required=False,
                default="python",
                enum=["python"],
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the find references operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            line = params["line"]
            column = params["column"]
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Find references using LSP
            references = await self.lsp_manager.find_references(
                file_path=file_path, line=line, column=column, language=language
            )

            # Format references for display
            formatted_references = []
            for ref in references:
                ref_info = {
                    "file": ref.get("relativePath", ref.get("absolutePath", "")),
                    "line": ref.get("range", {}).get("start", {}).get("line", 0),
                    "column": ref.get("range", {}).get("start", {}).get("character", 0),
                    "uri": ref.get("uri", ""),
                }

                # Try to get context around the reference
                try:
                    ref_file = ref.get("absolutePath", file_path)
                    if os.path.exists(ref_file):
                        with open(ref_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            ref_line = ref_info["line"]
                            if 0 <= ref_line < len(lines):
                                # Get some context around the reference
                                start_line = max(0, ref_line - 1)
                                end_line = min(len(lines), ref_line + 2)
                                context_lines = []
                                for i in range(start_line, end_line):
                                    prefix = ">>> " if i == ref_line else "    "
                                    context_lines.append(
                                        f"{prefix}{i+1:4d}: {lines[i].rstrip()}"
                                    )
                                ref_info["context"] = "\n".join(context_lines)
                except Exception:
                    ref_info["context"] = "<context unavailable>"

                formatted_references.append(ref_info)

            return ToolResult(
                success=True,
                data={
                    "query": {"file_path": file_path, "line": line, "column": column},
                    "reference_count": len(formatted_references),
                    "references": formatted_references,
                },
                metadata={"tool": "FindReferencesTool", "language": language},
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to find references: {e}")


class FindDefinitionTool(EmbeddedTool):
    """Find definition of a symbol at a specific position using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for finding definition."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file containing the symbol",
                required=True,
            ),
            ToolParameter(
                name="line",
                type=ParameterType.INTEGER,
                description="Line number (0-based) of the symbol",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="column",
                type=ParameterType.INTEGER,
                description="Column number (0-based) of the symbol",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="language",
                type=ParameterType.STRING,
                description="Programming language",
                required=False,
                default="python",
                enum=["python"],
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the find definition operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            line = params["line"]
            column = params["column"]
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Find definition using LSP
            definitions = await self.lsp_manager.find_definition(
                file_path=file_path, line=line, column=column, language=language
            )

            # Format definitions for display
            formatted_definitions = []
            for defn in definitions:
                defn_info = {
                    "file": defn.get("relativePath", defn.get("absolutePath", "")),
                    "line": defn.get("range", {}).get("start", {}).get("line", 0),
                    "column": defn.get("range", {})
                    .get("start", {})
                    .get("character", 0),
                    "uri": defn.get("uri", ""),
                }

                # Try to get context around the definition
                try:
                    defn_file = defn.get("absolutePath", file_path)
                    if os.path.exists(defn_file):
                        with open(defn_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            defn_line = defn_info["line"]
                            if 0 <= defn_line < len(lines):
                                # Get some context around the definition
                                start_line = max(0, defn_line - 1)
                                end_line = min(
                                    len(lines), defn_line + 5
                                )  # Show more context for definition
                                context_lines = []
                                for i in range(start_line, end_line):
                                    prefix = ">>> " if i == defn_line else "    "
                                    context_lines.append(
                                        f"{prefix}{i+1:4d}: {lines[i].rstrip()}"
                                    )
                                defn_info["context"] = "\n".join(context_lines)
                except Exception:
                    defn_info["context"] = "<context unavailable>"

                formatted_definitions.append(defn_info)

            return ToolResult(
                success=True,
                data={
                    "query": {"file_path": file_path, "line": line, "column": column},
                    "definition_count": len(formatted_definitions),
                    "definitions": formatted_definitions,
                },
                metadata={"tool": "FindDefinitionTool", "language": language},
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to find definition: {e}")


class GetDiagnosticsTool(EmbeddedTool):
    """Get diagnostics (errors, warnings) for a file using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for getting diagnostics."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file to analyze",
                required=True,
            ),
            ToolParameter(
                name="language",
                type=ParameterType.STRING,
                description="Programming language",
                required=False,
                default="python",
                enum=["python"],
            ),
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the get diagnostics operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Get diagnostics using LSP
            diagnostics = await self.lsp_manager.get_diagnostics(
                file_path=file_path, language=language
            )

            # Format diagnostics for display
            formatted_diagnostics = []
            for diag in diagnostics:
                severity_map = {1: "Error", 2: "Warning", 3: "Information", 4: "Hint"}

                diag_info = {
                    "message": diag.get("message", ""),
                    "severity": diag.get("severity", 1),
                    "severity_name": severity_map.get(
                        diag.get("severity", 1), "Unknown"
                    ),
                    "line": diag.get("range", {}).get("start", {}).get("line", 0),
                    "column": diag.get("range", {})
                    .get("start", {})
                    .get("character", 0),
                    "code": diag.get("code", ""),
                }

                # Try to get context around the diagnostic
                try:
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            diag_line = diag_info["line"]
                            if 0 <= diag_line < len(lines):
                                line_content = lines[diag_line].rstrip()
                                diag_info["line_content"] = line_content

                                # Show pointer to the column
                                pointer = " " * diag_info["column"] + "^"
                                diag_info["pointer"] = pointer
                except Exception:
                    diag_info["line_content"] = "<unavailable>"
                    diag_info["pointer"] = ""

                formatted_diagnostics.append(diag_info)

            # Count by severity
            error_count = sum(1 for d in formatted_diagnostics if d["severity"] == 1)
            warning_count = sum(1 for d in formatted_diagnostics if d["severity"] == 2)
            info_count = sum(1 for d in formatted_diagnostics if d["severity"] == 3)
            hint_count = sum(1 for d in formatted_diagnostics if d["severity"] == 4)

            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "total_diagnostics": len(formatted_diagnostics),
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "info_count": info_count,
                    "hint_count": hint_count,
                    "diagnostics": formatted_diagnostics,
                },
                metadata={"tool": "GetDiagnosticsTool", "language": language},
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get diagnostics: {e}")
