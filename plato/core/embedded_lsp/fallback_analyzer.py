"""
Fallback universal code analyzer for multiple programming languages.

This module provides comprehensive code analysis functionality when the solidlsp
library is not available. It uses Python's built-in ast module for Python code
and regex patterns for other languages.
"""

import ast
import logging
import os
import re
import keyword
import builtins
import importlib.util
import sys
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    """Symbol information."""

    name: str
    kind: int
    kind_name: str
    line: int
    column: int
    end_line: int
    end_column: int
    file: str
    body: Optional[str] = None
    docstring: Optional[str] = None
    type_hint: Optional[str] = None


class FallbackUniversalAnalyzer:
    """
    Universal code analyzer supporting multiple languages.

    Provides comprehensive code analysis functionality when solidlsp
    is not available. Supports Python (AST-based) and other languages
    (regex-based patterns).
    """

    def __init__(self):
        self.symbol_kinds = {
            ast.FunctionDef: 12,  # Function
            ast.AsyncFunctionDef: 12,  # Function
            ast.ClassDef: 5,  # Class
            ast.Assign: 13,  # Variable
            ast.AnnAssign: 13,  # Variable
            ast.Import: 2,  # Module
            ast.ImportFrom: 2,  # Module
        }

        # Symbol kind mapping
        self.SYMBOL_KINDS = {
            "File": 1,
            "Module": 2,
            "Namespace": 3,
            "Package": 4,
            "Class": 5,
            "Method": 6,
            "Property": 7,
            "Field": 8,
            "Constructor": 9,
            "Enum": 10,
            "Interface": 11,
            "Function": 12,
            "Variable": 13,
            "Constant": 14,
            "String": 15,
            "Number": 16,
            "Boolean": 17,
            "Array": 18,
            "Object": 19,
            "Key": 20,
            "Null": 21,
            "EnumMember": 22,
            "Struct": 23,
            "Event": 24,
            "Operator": 25,
            "TypeParameter": 26,
        }

        # Language detection patterns
        self.language_patterns = {
            "python": r"\.py$",
            "javascript": r"\.js$",
            "typescript": r"\.tsx?$",
            "go": r"\.go$",
            "java": r"\.java$",
            "rust": r"\.rs$",
            "cpp": r"\.(cpp|cc|cxx|c\+\+|hpp|h)$",
            "c": r"\.(c|h)$",
        }

        # Language-specific patterns for symbol detection
        self._init_language_patterns()

        # Workspace symbols cache
        self._workspace_cache = {}
        self._python_builtins = set(dir(builtins) + keyword.kwlist)

        # Definition cache for faster lookups
        self._definition_cache = {}

    def _init_language_patterns(self):
        """Initialize regex patterns for different languages."""
        # JavaScript/TypeScript patterns
        js_ts_patterns = {
            "function": r"(?:async\s+)?function\s+(\w+)\s*\(",
            "arrow_function": r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
            "class": r"class\s+(\w+)(?:\s+extends\s+\w+)?",
            "method": r"(?:async\s+)?(\w+)\s*\([^)]*\)\s*{",
            "variable": r"(?:const|let|var)\s+(\w+)\s*[=;]",
            "interface": r"interface\s+(\w+)",
            "type": r"type\s+(\w+)\s*=",
            "enum": r"enum\s+(\w+)",
        }

        # Go patterns
        go_patterns = {
            "function": r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(",
            "struct": r"type\s+(\w+)\s+struct",
            "interface": r"type\s+(\w+)\s+interface",
            "variable": r"(?:var|const)\s+(\w+)",
            "type": r"type\s+(\w+)\s+",
        }

        # Java patterns
        java_patterns = {
            "class": r"(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)",
            "interface": r"(?:public|private|protected)?\s*interface\s+(\w+)",
            "method": r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(",
            "field": r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*[;=]",
            "enum": r"(?:public|private|protected)?\s*enum\s+(\w+)",
        }

        # Rust patterns
        rust_patterns = {
            "function": r"fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(",
            "struct": r"struct\s+(\w+)",
            "enum": r"enum\s+(\w+)",
            "trait": r"trait\s+(\w+)",
            "impl": r"impl(?:\s+\w+)?\s+for\s+(\w+)",
            "const": r"const\s+(\w+):",
            "static": r"static\s+(\w+):",
        }

        self.language_patterns_symbols = {
            "javascript": js_ts_patterns,
            "typescript": js_ts_patterns,
            "go": go_patterns,
            "java": java_patterns,
            "rust": rust_patterns,
        }

    def detect_language(self, file_path: str) -> str:
        """Detect language based on file extension."""
        file_path = str(file_path)
        for lang, pattern in self.language_patterns.items():
            if re.search(pattern, file_path, re.IGNORECASE):
                return lang
        return "unknown"

    def get_symbols(
        self, file_path: str, include_body: bool = False, language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get symbols from a file using appropriate parsing method.

        Args:
            file_path: Path to the file
            include_body: Whether to include source code
            language: Programming language (auto-detected if not provided)

        Returns:
            List of symbol dictionaries
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            if language == "python":
                return self._get_python_symbols(file_path, include_body)
            else:
                return self._get_generic_symbols(file_path, language, include_body)

        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return []

    def _get_python_symbols(
        self, file_path: str, include_body: bool
    ) -> List[Dict[str, Any]]:
        """Get symbols from Python file using AST."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)
            symbols = []

            # Walk the AST and extract symbols with proper hierarchy
            for node in ast.walk(tree):
                symbol = self._node_to_symbol(node, source, include_body)
                if symbol:
                    symbols.append(symbol)

            # Cache for workspace symbols
            self._workspace_cache[file_path] = symbols

            return symbols

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to analyze Python file {file_path}: {e}")
            return []

    def _get_generic_symbols(
        self, file_path: str, language: str, include_body: bool
    ) -> List[Dict[str, Any]]:
        """Get symbols from non-Python files using regex patterns."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                lines = source.split("\n")

            symbols = []
            patterns = self.language_patterns_symbols.get(language, {})

            for pattern_name, pattern_regex in patterns.items():
                for match in re.finditer(pattern_regex, source, re.MULTILINE):
                    # Calculate line and column
                    start_pos = match.start()
                    line_num = source[:start_pos].count("\n")
                    line_start = source.rfind("\n", 0, start_pos) + 1
                    column = start_pos - line_start

                    symbol_name = match.group(1) if match.groups() else None
                    if not symbol_name:
                        continue

                    # Determine symbol kind
                    if pattern_name in ["function", "method", "arrow_function"]:
                        kind = self.SYMBOL_KINDS["Function"]
                        kind_name = "Function"
                    elif pattern_name in ["class", "struct"]:
                        kind = self.SYMBOL_KINDS["Class"]
                        kind_name = "Class"
                    elif pattern_name in ["interface", "trait"]:
                        kind = self.SYMBOL_KINDS["Interface"]
                        kind_name = "Interface"
                    elif pattern_name in ["variable", "field", "const", "static"]:
                        kind = self.SYMBOL_KINDS["Variable"]
                        kind_name = "Variable"
                    elif pattern_name == "enum":
                        kind = self.SYMBOL_KINDS["Enum"]
                        kind_name = "Enum"
                    elif pattern_name == "type":
                        kind = self.SYMBOL_KINDS["TypeParameter"]
                        kind_name = "TypeParameter"
                    else:
                        kind = self.SYMBOL_KINDS["Object"]
                        kind_name = "Object"

                    symbol_info = {
                        "name": symbol_name,
                        "kind": kind,
                        "kind_name": kind_name,
                        "range": {
                            "start": {"line": line_num, "character": column},
                            "end": {
                                "line": line_num,
                                "character": column + len(symbol_name),
                            },
                        },
                        "file": os.path.basename(file_path),
                        "absolutePath": file_path,
                    }

                    if include_body:
                        # Try to extract the body (simplified)
                        start_line = line_num
                        end_line = min(line_num + 10, len(lines))
                        body_lines = lines[start_line:end_line]
                        symbol_info["body"] = "\n".join(body_lines)

                    symbols.append(symbol_info)

            # Cache for workspace symbols
            self._workspace_cache[file_path] = symbols

            return symbols

        except Exception as e:
            logger.error(f"Failed to analyze {language} file {file_path}: {e}")
            return []

    def _node_to_symbol(
        self, node: ast.AST, source: str, include_body: bool
    ) -> Optional[Dict[str, Any]]:
        """Convert an AST node to a symbol dictionary."""
        if not hasattr(node, "lineno"):
            return None

        symbol_info = None

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbol_info = {
                "name": node.name,
                "kind": 12,  # Function
                "kind_name": "Function",
                "range": {
                    "start": {"line": node.lineno - 1, "character": node.col_offset},
                    "end": {
                        "line": (
                            node.end_lineno - 1 if node.end_lineno else node.lineno - 1
                        ),
                        "character": (
                            node.end_col_offset
                            if node.end_col_offset
                            else node.col_offset + len(node.name)
                        ),
                    },
                },
            }

            # Extract docstring
            docstring = ast.get_docstring(node)
            if docstring:
                symbol_info["docstring"] = docstring

            # Extract type hints
            if node.returns:
                try:
                    symbol_info["return_type"] = ast.unparse(node.returns)
                except:
                    pass

        elif isinstance(node, ast.ClassDef):
            symbol_info = {
                "name": node.name,
                "kind": 5,  # Class
                "kind_name": "Class",
                "range": {
                    "start": {"line": node.lineno - 1, "character": node.col_offset},
                    "end": {
                        "line": (
                            node.end_lineno - 1 if node.end_lineno else node.lineno - 1
                        ),
                        "character": (
                            node.end_col_offset
                            if node.end_col_offset
                            else node.col_offset + len(node.name)
                        ),
                    },
                },
            }

            # Extract docstring
            docstring = ast.get_docstring(node)
            if docstring:
                symbol_info["docstring"] = docstring

        elif isinstance(node, ast.Assign):
            # Handle simple variable assignments
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbol_info = {
                        "name": target.id,
                        "kind": 13,  # Variable
                        "kind_name": "Variable",
                        "range": {
                            "start": {
                                "line": node.lineno - 1,
                                "character": target.col_offset,
                            },
                            "end": {
                                "line": node.lineno - 1,
                                "character": target.col_offset + len(target.id),
                            },
                        },
                    }
                    break

        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            # Handle annotated assignments
            symbol_info = {
                "name": node.target.id,
                "kind": 13,  # Variable
                "kind_name": "Variable",
                "range": {
                    "start": {
                        "line": node.lineno - 1,
                        "character": node.target.col_offset,
                    },
                    "end": {
                        "line": node.lineno - 1,
                        "character": node.target.col_offset + len(node.target.id),
                    },
                },
            }

            # Extract type annotation
            if node.annotation:
                try:
                    symbol_info["type_hint"] = ast.unparse(node.annotation)
                except:
                    pass

        if symbol_info and include_body:
            # Extract source code for the symbol
            try:
                lines = source.split("\n")
                start_line = symbol_info["range"]["start"]["line"]
                end_line = symbol_info["range"]["end"]["line"]

                if start_line < len(lines):
                    if isinstance(
                        node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                    ):
                        # For functions/classes, get the whole definition
                        if hasattr(node, "end_lineno") and node.end_lineno:
                            body_lines = lines[start_line : node.end_lineno]
                        else:
                            # Fallback: just get a few lines
                            body_lines = lines[start_line : start_line + 5]
                        symbol_info["body"] = "\n".join(body_lines)
                    else:
                        # For variables, just get the line
                        symbol_info["body"] = lines[start_line]

            except Exception:
                symbol_info["body"] = "<body unavailable>"

        return symbol_info

    def find_definition(
        self, file_path: str, line: int, column: int, language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find definition of a symbol at the given position.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            List of definition locations
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            # Get the symbol at position
            symbol_name = self._get_symbol_at_position(file_path, line, column)
            if not symbol_name:
                return []

            definitions = []

            if language == "python":
                definitions = self._find_python_definition(
                    file_path, symbol_name, line, column
                )
            else:
                definitions = self._find_generic_definition(
                    file_path, symbol_name, language
                )

            return definitions

        except Exception as e:
            logger.error(f"Failed to find definition: {e}")
            return []

    def _find_python_definition(
        self, file_path: str, symbol_name: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Find Python symbol definition using AST."""
        definitions = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)

            # First, check if it's a builtin
            if symbol_name in self._python_builtins:
                return [
                    {
                        "file": "<builtin>",
                        "line": 0,
                        "column": 0,
                        "uri": "builtin://" + symbol_name,
                        "absolutePath": "<builtin>",
                        "relativePath": "<builtin>",
                        "builtin": True,
                    }
                ]

            # Look for definitions in the current file
            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    if node.name == symbol_name:
                        definitions.append(
                            {
                                "file": os.path.basename(file_path),
                                "line": node.lineno - 1,
                                "column": node.col_offset,
                                "uri": f"file://{file_path}",
                                "absolutePath": file_path,
                                "relativePath": os.path.basename(file_path),
                                "range": {
                                    "start": {
                                        "line": node.lineno - 1,
                                        "character": node.col_offset,
                                    },
                                    "end": {
                                        "line": node.lineno - 1,
                                        "character": node.col_offset + len(node.name),
                                    },
                                },
                            }
                        )
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == symbol_name:
                            # Check if this definition comes before the usage
                            if node.lineno - 1 <= line:
                                definitions.append(
                                    {
                                        "file": os.path.basename(file_path),
                                        "line": node.lineno - 1,
                                        "column": target.col_offset,
                                        "uri": f"file://{file_path}",
                                        "absolutePath": file_path,
                                        "relativePath": os.path.basename(file_path),
                                        "range": {
                                            "start": {
                                                "line": node.lineno - 1,
                                                "character": target.col_offset,
                                            },
                                            "end": {
                                                "line": node.lineno - 1,
                                                "character": target.col_offset
                                                + len(target.id),
                                            },
                                        },
                                    }
                                )
                elif isinstance(node, ast.AnnAssign):
                    if (
                        isinstance(node.target, ast.Name)
                        and node.target.id == symbol_name
                    ):
                        if node.lineno - 1 <= line:
                            definitions.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "line": node.lineno - 1,
                                    "column": node.target.col_offset,
                                    "uri": f"file://{file_path}",
                                    "absolutePath": file_path,
                                    "relativePath": os.path.basename(file_path),
                                    "range": {
                                        "start": {
                                            "line": node.lineno - 1,
                                            "character": node.target.col_offset,
                                        },
                                        "end": {
                                            "line": node.lineno - 1,
                                            "character": node.target.col_offset
                                            + len(node.target.id),
                                        },
                                    },
                                }
                            )

            # Look for imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.asname == symbol_name or (
                            not alias.asname and alias.name == symbol_name
                        ):
                            # This is an import, try to find the module
                            definitions.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "line": node.lineno - 1,
                                    "column": node.col_offset,
                                    "uri": f"file://{file_path}",
                                    "absolutePath": file_path,
                                    "relativePath": os.path.basename(file_path),
                                    "import": True,
                                    "module": alias.name,
                                }
                            )
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.asname == symbol_name or (
                            not alias.asname and alias.name == symbol_name
                        ):
                            definitions.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "line": node.lineno - 1,
                                    "column": node.col_offset,
                                    "uri": f"file://{file_path}",
                                    "absolutePath": file_path,
                                    "relativePath": os.path.basename(file_path),
                                    "import": True,
                                    "module": node.module,
                                    "name": alias.name,
                                }
                            )

            return definitions

        except Exception as e:
            logger.error(f"Failed to find Python definition: {e}")
            return []

    def _find_generic_definition(
        self, file_path: str, symbol_name: str, language: str
    ) -> List[Dict[str, Any]]:
        """Find definition in non-Python files using regex."""
        definitions = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                lines = source.split("\n")

            # Create pattern to find definition
            patterns = []

            if language in ["javascript", "typescript"]:
                patterns = [
                    rf"(?:const|let|var)\s+{re.escape(symbol_name)}\s*[=;]",
                    rf"function\s+{re.escape(symbol_name)}\s*\(",
                    rf"class\s+{re.escape(symbol_name)}(?:\s|$)",
                    rf"{re.escape(symbol_name)}\s*:\s*function\s*\(",
                ]
            elif language == "go":
                patterns = [
                    rf"func\s+(?:\(\w+\s+\*?\w+\)\s+)?{re.escape(symbol_name)}\s*\(",
                    rf"type\s+{re.escape(symbol_name)}\s+",
                    rf"(?:var|const)\s+{re.escape(symbol_name)}\s+",
                ]
            elif language == "java":
                patterns = [
                    rf"class\s+{re.escape(symbol_name)}(?:\s|$)",
                    rf"interface\s+{re.escape(symbol_name)}(?:\s|$)",
                    rf"\w+\s+{re.escape(symbol_name)}\s*[;=(]",
                ]
            elif language == "rust":
                patterns = [
                    rf"fn\s+{re.escape(symbol_name)}\s*(?:<[^>]+>)?\s*\(",
                    rf"struct\s+{re.escape(symbol_name)}(?:\s|$)",
                    rf"enum\s+{re.escape(symbol_name)}(?:\s|$)",
                    rf"(?:const|static)\s+{re.escape(symbol_name)}:",
                ]

            for pattern in patterns:
                for match in re.finditer(pattern, source, re.MULTILINE):
                    start_pos = match.start()
                    line_num = source[:start_pos].count("\n")
                    line_start = source.rfind("\n", 0, start_pos) + 1
                    column = start_pos - line_start

                    definitions.append(
                        {
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "column": column,
                            "uri": f"file://{file_path}",
                            "absolutePath": file_path,
                            "relativePath": os.path.basename(file_path),
                            "range": {
                                "start": {"line": line_num, "character": column},
                                "end": {
                                    "line": line_num,
                                    "character": column + len(symbol_name),
                                },
                            },
                        }
                    )

            return definitions

        except Exception as e:
            logger.error(f"Failed to find {language} definition: {e}")
            return []

    def find_references(
        self, file_path: str, line: int, column: int, language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find references to a symbol.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            List of reference locations
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            # Get the symbol at position
            symbol_name = self._get_symbol_at_position(file_path, line, column)
            if not symbol_name:
                return []

            return self.find_name_references(file_path, symbol_name, language)

        except Exception as e:
            logger.error(f"Failed to find references: {e}")
            return []

    def find_name_references(
        self, file_path: str, target_name: str, language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Find references to a name in the file.

        Args:
            file_path: Path to the file
            target_name: Name to search for
            language: Programming language

        Returns:
            List of reference locations
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
                lines = source.split("\n")

            references = []

            if language == "python":
                # Use AST for Python
                tree = ast.parse(source, filename=file_path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and node.id == target_name:
                        if hasattr(node, "lineno"):
                            references.append(
                                {
                                    "file": os.path.basename(file_path),
                                    "line": node.lineno - 1,
                                    "column": node.col_offset,
                                    "character": node.col_offset,  # Add character field
                                    "uri": f"file://{file_path}",
                                    "absolutePath": file_path,
                                    "relativePath": os.path.basename(file_path),
                                    "range": {
                                        "start": {
                                            "line": node.lineno - 1,
                                            "character": node.col_offset,
                                        },
                                        "end": {
                                            "line": node.lineno - 1,
                                            "character": node.col_offset
                                            + len(target_name),
                                        },
                                    },
                                }
                            )
            else:
                # Use regex for other languages
                # Create word boundary pattern
                pattern = rf"\b{re.escape(target_name)}\b"

                for match in re.finditer(pattern, source):
                    start_pos = match.start()
                    line_num = source[:start_pos].count("\n")
                    line_start = source.rfind("\n", 0, start_pos) + 1
                    column = start_pos - line_start

                    references.append(
                        {
                            "file": os.path.basename(file_path),
                            "line": line_num,
                            "column": column,
                            "character": column,  # Add character field
                            "uri": f"file://{file_path}",
                            "absolutePath": file_path,
                            "relativePath": os.path.basename(file_path),
                            "range": {
                                "start": {"line": line_num, "character": column},
                                "end": {
                                    "line": line_num,
                                    "character": column + len(target_name),
                                },
                            },
                        }
                    )

            return references

        except Exception as e:
            logger.error(f"Failed to find references in {file_path}: {e}")
            return []

    def get_hover_info(
        self, file_path: str, line: int, column: int, language: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get hover information for a symbol at the given position.

        Args:
            file_path: Path to the file
            line: Line number (0-based)
            column: Column number (0-based)
            language: Programming language

        Returns:
            Hover information or None
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            # Get the symbol at position
            symbol_name = self._get_symbol_at_position(file_path, line, column)
            if not symbol_name:
                return None

            hover_info = {
                "contents": "",
                "range": {
                    "start": {"line": line, "character": column},
                    "end": {"line": line, "character": column + len(symbol_name)},
                },
            }

            if language == "python":
                # Try to get Python-specific info
                hover_info["contents"] = self._get_python_hover_info(
                    file_path, symbol_name, line, column
                )
            else:
                # Generic hover info
                hover_info["contents"] = f"{symbol_name} ({language})"

            return hover_info

        except Exception as e:
            logger.error(f"Failed to get hover info: {e}")
            return None

    def _get_python_hover_info(
        self, file_path: str, symbol_name: str, line: int, column: int
    ) -> str:
        """Get Python-specific hover information."""
        try:
            # Check if it's a builtin
            if symbol_name in self._python_builtins:
                if symbol_name in dir(builtins):
                    obj = getattr(builtins, symbol_name)
                    if callable(obj) and obj.__doc__:
                        return f"```python\n{symbol_name}\n```\n\n{obj.__doc__}"
                return f"```python\n{symbol_name}\n```\n\nBuilt-in {symbol_name}"

            # Try to find the symbol definition
            definitions = self._find_python_definition(
                file_path, symbol_name, line, column
            )
            if definitions:
                defn = definitions[0]

                # Try to get more info from the definition
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()

                tree = ast.parse(source, filename=file_path)

                for node in ast.walk(tree):
                    if hasattr(node, "name") and node.name == symbol_name:
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Build function signature
                            sig = f"def {node.name}("
                            args = []
                            for arg in node.args.args:
                                arg_str = arg.arg
                                if arg.annotation:
                                    try:
                                        arg_str += f": {ast.unparse(arg.annotation)}"
                                    except:
                                        pass
                                args.append(arg_str)
                            sig += ", ".join(args) + ")"
                            if node.returns:
                                try:
                                    sig += f" -> {ast.unparse(node.returns)}"
                                except:
                                    pass

                            docstring = (
                                ast.get_docstring(node) or "No documentation available"
                            )
                            return f"```python\n{sig}\n```\n\n{docstring}"

                        elif isinstance(node, ast.ClassDef):
                            docstring = (
                                ast.get_docstring(node) or "No documentation available"
                            )
                            return f"```python\nclass {node.name}\n```\n\n{docstring}"

            # Default
            return f"```python\n{symbol_name}\n```"

        except Exception as e:
            logger.error(f"Failed to get Python hover info: {e}")
            return symbol_name

    def get_completions(
        self, file_path: str, line: int, column: int, language: str = None
    ) -> List[Dict[str, Any]]:
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
        try:
            if not language:
                language = self.detect_language(file_path)

            completions = []

            # Get partial text at cursor
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if 0 <= line < len(lines):
                line_text = lines[line]
                partial = self._get_partial_at_position(line_text, column)

                if language == "python":
                    completions = self._get_python_completions(
                        file_path, partial, line, column
                    )
                else:
                    completions = self._get_generic_completions(language, partial)

            return completions

        except Exception as e:
            logger.error(f"Failed to get completions: {e}")
            return []

    def _get_partial_at_position(self, line_text: str, column: int) -> str:
        """Get the partial word at the cursor position."""
        if column <= 0:
            return ""

        # Find the start of the word
        start = column
        while start > 0 and (
            line_text[start - 1].isalnum() or line_text[start - 1] == "_"
        ):
            start -= 1

        return line_text[start:column]

    def _get_python_completions(
        self, file_path: str, partial: str, line: int, column: int
    ) -> List[Dict[str, Any]]:
        """Get Python-specific completions."""
        completions = []

        try:
            # Add Python keywords
            for kw in keyword.kwlist:
                if kw.startswith(partial):
                    completions.append(
                        {
                            "label": kw,
                            "kind": 14,  # Keyword
                            "detail": "keyword",
                            "insertText": kw,
                        }
                    )

            # Add builtins
            for builtin_name in dir(builtins):
                if builtin_name.startswith(partial) and not builtin_name.startswith(
                    "_"
                ):
                    completions.append(
                        {
                            "label": builtin_name,
                            "kind": 3,  # Function/Class
                            "detail": "builtin",
                            "insertText": builtin_name,
                        }
                    )

            # Add symbols from current file
            symbols = self.get_symbols(file_path, False, "python")
            for symbol in symbols:
                if symbol["name"].startswith(partial):
                    completions.append(
                        {
                            "label": symbol["name"],
                            "kind": symbol["kind"],
                            "detail": symbol.get("kind_name", ""),
                            "insertText": symbol["name"],
                        }
                    )

            return completions

        except Exception as e:
            logger.error(f"Failed to get Python completions: {e}")
            return []

    def _get_generic_completions(
        self, language: str, partial: str
    ) -> List[Dict[str, Any]]:
        """Get generic completions for non-Python languages."""
        completions = []

        # Language-specific keywords
        keywords = {
            "javascript": [
                "const",
                "let",
                "var",
                "function",
                "class",
                "if",
                "else",
                "for",
                "while",
                "return",
                "async",
                "await",
                "import",
                "export",
                "default",
                "new",
                "this",
            ],
            "typescript": [
                "const",
                "let",
                "var",
                "function",
                "class",
                "interface",
                "type",
                "enum",
                "if",
                "else",
                "for",
                "while",
                "return",
                "async",
                "await",
                "import",
                "export",
                "default",
                "new",
                "this",
                "public",
                "private",
                "protected",
            ],
            "go": [
                "func",
                "var",
                "const",
                "type",
                "struct",
                "interface",
                "if",
                "else",
                "for",
                "range",
                "return",
                "defer",
                "go",
                "chan",
                "select",
                "case",
                "default",
            ],
            "java": [
                "public",
                "private",
                "protected",
                "class",
                "interface",
                "enum",
                "extends",
                "implements",
                "if",
                "else",
                "for",
                "while",
                "return",
                "new",
                "this",
                "super",
                "static",
                "final",
                "abstract",
            ],
            "rust": [
                "fn",
                "let",
                "mut",
                "const",
                "struct",
                "enum",
                "trait",
                "impl",
                "if",
                "else",
                "for",
                "while",
                "loop",
                "match",
                "return",
                "use",
                "mod",
                "pub",
                "self",
            ],
        }

        lang_keywords = keywords.get(language, [])
        for kw in lang_keywords:
            if kw.startswith(partial):
                completions.append(
                    {
                        "label": kw,
                        "kind": 14,  # Keyword
                        "detail": "keyword",
                        "insertText": kw,
                    }
                )

        return completions

    def get_diagnostics(
        self, file_path: str, language: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get diagnostics (errors, warnings) for a file.

        Args:
            file_path: Path to the file
            language: Programming language

        Returns:
            List of diagnostics
        """
        try:
            if not language:
                language = self.detect_language(file_path)

            if language == "python":
                return self.get_basic_diagnostics(file_path)
            else:
                return self._get_generic_diagnostics(file_path, language)

        except Exception as e:
            logger.error(f"Failed to get diagnostics: {e}")
            return []

    def get_basic_diagnostics(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get basic syntax diagnostics using AST parsing.

        Args:
            file_path: Path to the Python file

        Returns:
            List of diagnostic dictionaries
        """
        diagnostics = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            # Try to parse the file
            try:
                tree = ast.parse(source, filename=file_path)

                # If parsing succeeds, perform additional checks
                diagnostics.extend(self._check_python_style(source, tree))

            except SyntaxError as e:
                # Return syntax error as diagnostic
                diagnostics.append(
                    {
                        "message": f"SyntaxError: {e.msg}",
                        "severity": 1,  # Error
                        "severity_name": "Error",
                        "range": {
                            "start": {
                                "line": (e.lineno or 1) - 1,
                                "character": (e.offset or 1) - 1,
                            },
                            "end": {
                                "line": (e.lineno or 1) - 1,
                                "character": (e.offset or 1) - 1,
                            },
                        },
                        "code": "syntax-error",
                    }
                )

            return diagnostics

        except Exception as e:
            logger.error(f"Failed to check diagnostics for {file_path}: {e}")
            return []

    def _check_python_style(self, source: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Check Python code style and common issues."""
        diagnostics = []
        lines = source.split("\n")

        # Check for common issues
        for node in ast.walk(tree):
            # Check for undefined names (simplified)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # This is a very simplified check
                if node.id not in self._python_builtins and hasattr(node, "lineno"):
                    # Check if it's defined before use (very basic)
                    is_defined = False
                    for other_node in ast.walk(tree):
                        if isinstance(other_node, (ast.FunctionDef, ast.ClassDef)):
                            if (
                                other_node.name == node.id
                                and other_node.lineno <= node.lineno
                            ):
                                is_defined = True
                                break

                    if not is_defined and node.id not in ["self", "cls"]:
                        diagnostics.append(
                            {
                                "message": f"Name '{node.id}' may be undefined",
                                "severity": 2,  # Warning
                                "severity_name": "Warning",
                                "range": {
                                    "start": {
                                        "line": node.lineno - 1,
                                        "character": node.col_offset,
                                    },
                                    "end": {
                                        "line": node.lineno - 1,
                                        "character": node.col_offset + len(node.id),
                                    },
                                },
                                "code": "undefined-name",
                            }
                        )

        # Check line length
        for i, line in enumerate(lines):
            if len(line) > 120:
                diagnostics.append(
                    {
                        "message": f"Line too long ({len(line)} > 120 characters)",
                        "severity": 3,  # Information
                        "severity_name": "Information",
                        "range": {
                            "start": {"line": i, "character": 120},
                            "end": {"line": i, "character": len(line)},
                        },
                        "code": "line-too-long",
                    }
                )

        return diagnostics

    def _get_generic_diagnostics(
        self, file_path: str, language: str
    ) -> List[Dict[str, Any]]:
        """Get basic diagnostics for non-Python files."""
        diagnostics = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Basic checks
            for i, line in enumerate(lines):
                # Check line length
                if len(line.rstrip()) > 120:
                    diagnostics.append(
                        {
                            "message": f"Line too long ({len(line.rstrip())} > 120 characters)",
                            "severity": 3,  # Information
                            "severity_name": "Information",
                            "range": {
                                "start": {"line": i, "character": 120},
                                "end": {"line": i, "character": len(line.rstrip())},
                            },
                            "code": "line-too-long",
                        }
                    )

                # Check for TODO/FIXME comments
                if "TODO" in line or "FIXME" in line:
                    match = re.search(r"(TODO|FIXME)", line)
                    if match:
                        diagnostics.append(
                            {
                                "message": f"{match.group(1)} comment found",
                                "severity": 3,  # Information
                                "severity_name": "Information",
                                "range": {
                                    "start": {"line": i, "character": match.start()},
                                    "end": {"line": i, "character": match.end()},
                                },
                                "code": "todo-comment",
                            }
                        )

            return diagnostics

        except Exception as e:
            logger.error(f"Failed to get {language} diagnostics: {e}")
            return []

    def workspace_symbols(
        self, query: str, workspace_root: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for symbols across the workspace.

        Args:
            query: Search query
            workspace_root: Root directory to search in

        Returns:
            List of matching symbols
        """
        try:
            if not workspace_root:
                workspace_root = os.getcwd()

            matching_symbols = []
            query_lower = query.lower()

            # Search through all cached files first
            for file_path, symbols in self._workspace_cache.items():
                for symbol in symbols:
                    if query_lower in symbol.get("name", "").lower():
                        matching_symbols.append(symbol)

            # If cache is empty, scan workspace
            if not matching_symbols:
                for root, dirs, files in os.walk(workspace_root):
                    # Skip common directories
                    dirs[:] = [
                        d
                        for d in dirs
                        if d
                        not in [".git", "__pycache__", "node_modules", ".venv", "venv"]
                    ]

                    for file in files:
                        file_path = os.path.join(root, file)
                        language = self.detect_language(file_path)

                        if language != "unknown":
                            symbols = self.get_symbols(file_path, False, language)
                            for symbol in symbols:
                                if query_lower in symbol.get("name", "").lower():
                                    symbol["file"] = file_path
                                    matching_symbols.append(symbol)

            return matching_symbols[:50]  # Limit results

        except Exception as e:
            logger.error(f"Failed to search workspace symbols: {e}")
            return []

    def call_hierarchy(
        self, file_path: str, line: int, column: int, language: str = None
    ) -> Dict[str, Any]:
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
        try:
            if not language:
                language = self.detect_language(file_path)

            # Get the symbol at position
            symbol_name = self._get_symbol_at_position(file_path, line, column)
            if not symbol_name:
                return {}

            hierarchy = {
                "name": symbol_name,
                "file": file_path,
                "line": line,
                "column": column,
                "incoming_calls": [],
                "outgoing_calls": [],
            }

            if language == "python":
                hierarchy.update(
                    self._get_python_call_hierarchy(
                        file_path, symbol_name, line, column
                    )
                )

            return hierarchy

        except Exception as e:
            logger.error(f"Failed to get call hierarchy: {e}")
            return {}

    def _get_python_call_hierarchy(
        self, file_path: str, function_name: str, line: int, column: int
    ) -> Dict[str, Any]:
        """Get Python-specific call hierarchy."""
        hierarchy = {"incoming_calls": [], "outgoing_calls": []}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=file_path)

            # Find the target function
            target_func = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == function_name and node.lineno - 1 == line:
                        target_func = node
                        break

            if target_func:
                # Find outgoing calls (functions called by this function)
                for node in ast.walk(target_func):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            hierarchy["outgoing_calls"].append(
                                {
                                    "name": node.func.id,
                                    "line": node.lineno - 1,
                                    "column": node.col_offset,
                                }
                            )
                        elif isinstance(node.func, ast.Attribute):
                            hierarchy["outgoing_calls"].append(
                                {
                                    "name": node.func.attr,
                                    "line": node.lineno - 1,
                                    "column": node.col_offset,
                                }
                            )

            # Find incoming calls (functions that call this function)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node != target_func:
                        for call_node in ast.walk(node):
                            if isinstance(call_node, ast.Call):
                                if (
                                    isinstance(call_node.func, ast.Name)
                                    and call_node.func.id == function_name
                                ):
                                    hierarchy["incoming_calls"].append(
                                        {
                                            "name": node.name,
                                            "line": node.lineno - 1,
                                            "column": node.col_offset,
                                        }
                                    )

            return hierarchy

        except Exception as e:
            logger.error(f"Failed to get Python call hierarchy: {e}")
            return hierarchy

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
                        line_text[start - 1].isalnum() or line_text[start - 1] in "_"
                    ):
                        start -= 1

                    # Find the end of the identifier
                    end = column
                    while end < len(line_text) and (
                        line_text[end].isalnum() or line_text[end] in "_"
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


# Maintain backward compatibility
FallbackPythonAnalyzer = FallbackUniversalAnalyzer
