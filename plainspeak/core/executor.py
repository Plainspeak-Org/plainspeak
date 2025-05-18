"""
Command Executor for PlainSpeak.

This module provides command execution functionality with safety checks,
error handling, and execution result tracking.
"""

import logging
from typing import Optional, Tuple

from ..context import session_context
from .sandbox import Sandbox

logger = logging.getLogger(__name__)


class CommandExecutor:
    """
    Handles safe execution of commands with result tracking.
    Integrates with session context and sandbox for safety.
    """

    def __init__(self, sandbox: Optional[Sandbox] = None):
        """
        Initialize the command executor.

        Args:
            sandbox: Optional custom sandbox instance. If not provided,
                    a new Sandbox instance will be created.
        """
        self.sandbox = sandbox or Sandbox()

    def execute(
        self, command: str, original_text: Optional[str] = None, track_history: bool = True
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Execute a command safely and track results.

        Args:
            command: The command to execute
            original_text: Original natural language text (for history)
            track_history: Whether to track in session history

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            returncode, stdout, stderr = self.sandbox.execute_shell_command(command)
            success = returncode == 0

            if track_history and original_text:
                session_context.add_to_history(original_text, command, success)

            return success, stdout, stderr

        except Exception as e:
            logger.error("Command execution failed: %s", str(e))
            if track_history and original_text:
                session_context.add_to_history(original_text, command, False)
            return False, None, str(e)

    def execute_safe(self, command: str, original_text: Optional[str] = None, track_history: bool = True) -> bool:
        """
        Execute a command safely and return only success status.
        Simplified interface that doesn't expose output streams.

        Args:
            command: The command to execute
            original_text: Original natural language text (for history)
            track_history: Whether to track in session history

        Returns:
            True if command succeeded, False otherwise
        """
        success, _, _ = self.execute(command, original_text=original_text, track_history=track_history)
        return success
