"""
Code analysis tools using embedded LSP capabilities.

These tools provide advanced code analysis features like hover information,
code completions, and comprehensive code analysis.
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


class HoverInfoTool(EmbeddedTool):
    """Get hover information for a symbol at a specific position using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for getting hover information."""
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
        """Execute the hover info operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            line = params["line"]
            column = params["column"]
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Get hover info using LSP
            hover = await self.lsp_manager.get_hover_info(
                file_path=file_path, line=line, column=column, language=language
            )

            if not hover:
                return ToolResult(
                    success=True,
                    data={
                        "query": {
                            "file_path": file_path,
                            "line": line,
                            "column": column,
                        },
                        "hover_available": False,
                        "message": "No hover information available at this position",
                    },
                    metadata={"tool": "HoverInfoTool", "language": language},
                )

            # Format hover information
            contents = hover.get("contents", "")
            hover_text = ""

            if isinstance(contents, str):
                hover_text = contents
            elif isinstance(contents, dict):
                hover_text = contents.get("value", str(contents))
            elif isinstance(contents, list):
                hover_text = "\n".join(str(item) for item in contents)
            else:
                hover_text = str(contents)

            # Try to get context around the position
            context = ""
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= line < len(lines):
                        line_content = lines[line].rstrip()
                        pointer = " " * column + "^"
                        context = f"{line+1:4d}: {line_content}\n      {pointer}"
            except Exception:
                context = "<context unavailable>"

            return ToolResult(
                success=True,
                data={
                    "query": {"file_path": file_path, "line": line, "column": column},
                    "hover_available": True,
                    "hover_text": hover_text,
                    "context": context,
                },
                metadata={"tool": "HoverInfoTool", "language": language},
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get hover info: {e}")


class CompletionsTool(EmbeddedTool):
    """Get code completions at a specific position using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for getting completions."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file",
                required=True,
            ),
            ToolParameter(
                name="line",
                type=ParameterType.INTEGER,
                description="Line number (0-based) for completions",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="column",
                type=ParameterType.INTEGER,
                description="Column number (0-based) for completions",
                required=True,
                min_value=0,
            ),
            ToolParameter(
                name="max_results",
                type=ParameterType.INTEGER,
                description="Maximum number of completion results to return",
                required=False,
                default=20,
                min_value=1,
                max_value=100,
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
        """Execute the completions operation."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            line = params["line"]
            column = params["column"]
            max_results = params.get("max_results", 20)
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            # Get completions using LSP
            completions = await self.lsp_manager.get_completions(
                file_path=file_path, line=line, column=column, language=language
            )

            # Format completions for display
            formatted_completions = []
            for i, comp in enumerate(completions[:max_results]):
                completion_kinds = {
                    1: "Text",
                    2: "Method",
                    3: "Function",
                    4: "Constructor",
                    5: "Field",
                    6: "Variable",
                    7: "Class",
                    8: "Interface",
                    9: "Module",
                    10: "Property",
                    11: "Unit",
                    12: "Value",
                    13: "Enum",
                    14: "Keyword",
                    15: "Snippet",
                    16: "Color",
                    17: "File",
                    18: "Reference",
                    19: "Folder",
                    20: "EnumMember",
                    21: "Constant",
                    22: "Struct",
                    23: "Event",
                    24: "Operator",
                    25: "TypeParameter",
                }

                comp_info = {
                    "completion_text": comp.get(
                        "completionText", comp.get("label", "")
                    ),
                    "kind": comp.get("kind", 1),
                    "kind_name": completion_kinds.get(comp.get("kind", 1), "Unknown"),
                    "detail": comp.get("detail", ""),
                }

                formatted_completions.append(comp_info)

            # Try to get context around the completion position
            context = ""
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= line < len(lines):
                        line_content = lines[line].rstrip()
                        pointer = " " * column + "^"
                        context = f"{line+1:4d}: {line_content}\n      {pointer}"
            except Exception:
                context = "<context unavailable>"

            return ToolResult(
                success=True,
                data={
                    "query": {"file_path": file_path, "line": line, "column": column},
                    "completion_count": len(formatted_completions),
                    "total_available": len(completions),
                    "showing_top": max_results,
                    "completions": formatted_completions,
                    "context": context,
                },
                metadata={"tool": "CompletionsTool", "language": language},
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to get completions: {e}")


class CodeAnalysisTool(EmbeddedTool):
    """Comprehensive code analysis for a file using LSP."""

    def __init__(self):
        super().__init__()
        self.lsp_manager = LSPManager()

    def _define_parameters(self) -> List[ToolParameter]:
        """Define parameters for code analysis."""
        return [
            ToolParameter(
                name="file_path",
                type=ParameterType.FILE_PATH,
                description="Path to the file to analyze",
                required=True,
            ),
            ToolParameter(
                name="include_symbols",
                type=ParameterType.BOOLEAN,
                description="Include symbol analysis in results",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="include_diagnostics",
                type=ParameterType.BOOLEAN,
                description="Include diagnostic analysis in results",
                required=False,
                default=True,
            ),
            ToolParameter(
                name="include_symbol_bodies",
                type=ParameterType.BOOLEAN,
                description="Include symbol source code in results",
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
        """Execute comprehensive code analysis."""
        try:
            params = self.validate_parameters(**kwargs)
            file_path = params["file_path"]
            include_symbols = params.get("include_symbols", True)
            include_diagnostics = params.get("include_diagnostics", True)
            include_symbol_bodies = params.get("include_symbol_bodies", False)
            language = params.get("language", "python")

            # Check if file exists
            if not os.path.exists(file_path):
                raise ToolError(f"File not found: {file_path}")

            analysis_results = {
                "file_path": file_path,
                "language": language,
            }

            # Get file stats
            try:
                stat = os.stat(file_path)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                analysis_results["file_stats"] = {
                    "size_bytes": stat.st_size,
                    "line_count": len(lines),
                    "character_count": len(content),
                    "non_empty_lines": len([line for line in lines if line.strip()]),
                }
            except Exception as e:
                analysis_results["file_stats"] = {"error": str(e)}

            # Get symbols if requested
            if include_symbols:
                try:
                    symbols = await self.lsp_manager.get_symbols(
                        file_path=file_path,
                        include_body=include_symbol_bodies,
                        language=language,
                    )

                    # Categorize symbols
                    symbol_categories = {}
                    for symbol in symbols:
                        kind_name = self._get_symbol_kind_name(symbol.get("kind", 0))
                        if kind_name not in symbol_categories:
                            symbol_categories[kind_name] = []

                        symbol_info = {
                            "name": symbol.get("name", ""),
                            "line": symbol.get("range", {})
                            .get("start", {})
                            .get("line", 0),
                        }

                        if include_symbol_bodies and "body" in symbol:
                            symbol_info["body"] = symbol["body"]

                        symbol_categories[kind_name].append(symbol_info)

                    analysis_results["symbols"] = {
                        "total_count": len(symbols),
                        "categories": symbol_categories,
                        "summary": {
                            category: len(items)
                            for category, items in symbol_categories.items()
                        },
                    }

                except Exception as e:
                    analysis_results["symbols"] = {"error": str(e)}

            # Get diagnostics if requested
            if include_diagnostics:
                try:
                    diagnostics = await self.lsp_manager.get_diagnostics(
                        file_path=file_path, language=language
                    )

                    # Categorize diagnostics
                    severity_map = {
                        1: "errors",
                        2: "warnings",
                        3: "information",
                        4: "hints",
                    }
                    diagnostic_categories = {
                        "errors": [],
                        "warnings": [],
                        "information": [],
                        "hints": [],
                    }

                    for diag in diagnostics:
                        severity = diag.get("severity", 1)
                        category = severity_map.get(severity, "errors")

                        diag_info = {
                            "message": diag.get("message", ""),
                            "line": diag.get("range", {})
                            .get("start", {})
                            .get("line", 0),
                            "column": diag.get("range", {})
                            .get("start", {})
                            .get("character", 0),
                            "code": diag.get("code", ""),
                        }

                        diagnostic_categories[category].append(diag_info)

                    analysis_results["diagnostics"] = {
                        "total_count": len(diagnostics),
                        "categories": diagnostic_categories,
                        "summary": {
                            "error_count": len(diagnostic_categories["errors"]),
                            "warning_count": len(diagnostic_categories["warnings"]),
                            "info_count": len(diagnostic_categories["information"]),
                            "hint_count": len(diagnostic_categories["hints"]),
                        },
                    }

                except Exception as e:
                    analysis_results["diagnostics"] = {"error": str(e)}

            # Generate analysis summary
            summary = []
            if "file_stats" in analysis_results:
                stats = analysis_results["file_stats"]
                if "line_count" in stats:
                    summary.append(
                        f"File has {stats['line_count']} lines ({stats['non_empty_lines']} non-empty)"
                    )

            if (
                "symbols" in analysis_results
                and "summary" in analysis_results["symbols"]
            ):
                symbol_summary = analysis_results["symbols"]["summary"]
                if symbol_summary:
                    symbol_items = [
                        f"{count} {category.lower()}"
                        for category, count in symbol_summary.items()
                    ]
                    summary.append(f"Contains: {', '.join(symbol_items)}")

            if (
                "diagnostics" in analysis_results
                and "summary" in analysis_results["diagnostics"]
            ):
                diag_summary = analysis_results["diagnostics"]["summary"]
                issues = []
                if diag_summary["error_count"] > 0:
                    issues.append(f"{diag_summary['error_count']} errors")
                if diag_summary["warning_count"] > 0:
                    issues.append(f"{diag_summary['warning_count']} warnings")

                if issues:
                    summary.append(f"Issues found: {', '.join(issues)}")
                else:
                    summary.append("No issues found")

            analysis_results["summary"] = summary

            return ToolResult(
                success=True,
                data=analysis_results,
                metadata={
                    "tool": "CodeAnalysisTool",
                    "language": language,
                    "analysis_time": "N/A",  # Could add timing if needed
                },
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"Failed to analyze code: {e}")

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
