"""Plato: AI orchestration system with MCP integration."""

__version__ = "0.1.0"
__author__ = "Claude Code"
__email__ = "noreply@anthropic.com"

from plato.core.ai_router import AIRouter
from plato.core.context_manager import ContextManager
from plato.core.mcp_manager import MCPManager

# Optional Serena MCP integration
try:
    from plato.integrations.serena_mcp import SerenaMCPClient

    _SERENA_AVAILABLE = True
except ImportError:
    SerenaMCPClient = None
    _SERENA_AVAILABLE = False

__all__ = [
    "AIRouter",
    "ContextManager",
    "MCPManager",
]

if _SERENA_AVAILABLE:
    __all__.append("SerenaMCPClient")
