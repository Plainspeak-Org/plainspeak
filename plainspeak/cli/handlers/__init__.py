"""
Command handler modules for the PlainSpeak Shell.

This package contains handler modules for different command types.
"""

from .execution_handlers import handle_bang, handle_exec, handle_execute
from .system_handlers import handle_context, handle_export, handle_history, handle_learning, handle_plugins
from .translate_handlers import handle_translate

__all__ = [
    "handle_translate",
    "handle_execute",
    "handle_bang",
    "handle_exec",
    "handle_context",
    "handle_export",
    "handle_history",
    "handle_learning",
    "handle_plugins",
]
