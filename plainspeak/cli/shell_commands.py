"""
Command handlers for the PlainSpeak Shell.

This module provides the command handler methods for the PlainSpeak interactive shell.
This is a facade module that re-exports handlers from the specialized modules.
"""

# Re-export handlers from specialized modules
from .handlers.execution_handlers import handle_bang, handle_exec, handle_execute
from .handlers.system_handlers import handle_context, handle_export, handle_history, handle_learning, handle_plugins
from .handlers.translate_handlers import handle_translate

# Define what to export when `from shell_commands import *` is used
__all__ = [
    "handle_translate",
    "handle_execute",
    "handle_history",
    "handle_context",
    "handle_learning",
    "handle_export",
    "handle_plugins",
    "handle_exec",
    "handle_bang",
]
