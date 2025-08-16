"""
Embedded LSP (Language Server Protocol) integration for Plato.

This module provides LSP capabilities directly embedded into Plato without
requiring a separate server process. It uses the solidlsp library from Serena
to provide code analysis features like symbol navigation, reference finding,
definition lookup, and diagnostics.

Key components:
- LSPManager: Main interface for LSP operations
- SymbolTools: Tools for symbol-based operations
- CodeAnalysisTools: Tools for code analysis and diagnostics
"""

from .lsp_manager import LSPManager
from .symbol_tools import (
    GetSymbolsTool,
    FindReferencesTool,
    FindDefinitionTool,
    GetDiagnosticsTool,
)
from .code_analysis import (
    CodeAnalysisTool,
    HoverInfoTool,
    CompletionsTool,
)

__all__ = [
    "LSPManager",
    "GetSymbolsTool",
    "FindReferencesTool",
    "FindDefinitionTool",
    "GetDiagnosticsTool",
    "CodeAnalysisTool",
    "HoverInfoTool",
    "CompletionsTool",
]
