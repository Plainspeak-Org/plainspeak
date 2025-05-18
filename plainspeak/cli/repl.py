"""
REPL interface for PlainSpeak.

This module provides a REPL (Read-Eval-Print Loop) interface
that allows interactive command translation.
"""

import sys

from rich.console import Console

from ..context import session_context
from . import PlainSpeakShell  # Use relative import from current package

console = Console()


class REPLInterface:
    """
    REPL interface that wraps PlainSpeakShell functionality.
    Provides interactive command translation interface.
    """

    def __init__(self):
        """Initialize the REPL interface."""
        self.shell = PlainSpeakShell()

    def start(self):
        """Start the REPL session."""
        try:
            return self.shell.cmdloop()
        except KeyboardInterrupt:
            console.print("\nExiting shell...", style="yellow")
            self._cleanup()
            sys.exit(0)
        except Exception as e:
            console.print(f"\nError in shell: {e}", style="red")
            self._cleanup()
            sys.exit(1)

    def _cleanup(self):
        """Cleanup resources before exiting."""
        try:
            session_context.save_context()
        except Exception as e:
            console.print(f"Error saving context: {e}", style="red")
