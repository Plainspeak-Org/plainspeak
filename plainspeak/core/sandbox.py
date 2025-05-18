"""
Safety Sandbox for PlainSpeak.

This module provides enhanced safety mechanisms for command execution.
"""

import logging
import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

from ..plugins.platform import platform_manager

logger = logging.getLogger(__name__)


@dataclass
class CommandContext:
    """Context information for command execution."""

    command: str
    cwd: str
    env: Dict[str, str]
    user: str
    timestamp: datetime
    platform: str


class SandboxExecutionError(Exception):
    """Raised when sandbox execution fails."""


class Sandbox:
    """
    Enhanced safety sandbox for command execution.

    Features:
    - Command whitelisting/blacklisting
    - Resource limiting
    - Platform-specific safety checks
    - Detailed logging
    """

    # Commands that are never allowed
    BLACKLISTED_COMMANDS = {
        "rm -rf /",  # Prevent root deletion
        "dd",  # Raw disk operations
        "mkfs",  # Filesystem formatting
        ":(){:|:&}",  # Fork bomb
        "wget",  # Arbitrary downloads (use controlled plugin instead)
        "curl",  # Arbitrary downloads (use controlled plugin instead)
    }

    # Patterns that indicate potentially dangerous operations
    DANGEROUS_PATTERNS = [
        r"\brm\s+(-[rf]\s+)*/*\s*$",  # Risky remove commands
        r"\b(dd|mkfs|fdisk)\b",  # Disk operations
        r"\b(wget|curl)\s+http",  # Arbitrary downloads
        r">[>&]?(/etc|/dev|/sys)",  # Writing to system directories
        r"\b(chmod|chown)\s+[0-7]*777\b",  # Overly permissive permissions
    ]

    # Resource limits (0 = unlimited)
    RESOURCE_LIMITS = {
        "MAX_CPU_TIME": 60,  # seconds
        "MAX_MEMORY": 512,  # MB
        "MAX_OUTPUT": 10_000,  # lines
        "MAX_PROCESSES": 10,  # subprocesses
    }

    def __init__(self):
        """Initialize the safety sandbox."""
        self.platform_mgr = platform_manager

    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a command is safe to execute.

        Args:
            command: The command to validate.

        Returns:
            Tuple of (is_safe, error_message).
        """
        # Check blacklisted commands
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return False, "Empty command"

        # Check against blacklist
        if command in self.BLACKLISTED_COMMANDS:
            return False, f"Command '{command}' is blacklisted"

        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                return False, f"Command matches dangerous pattern: {pattern}"

        # Platform-specific path checks
        for part in cmd_parts:
            # Convert potential paths to normalized form
            if os.path.sep in part or "/" in part:
                if not self.platform_mgr.is_safe_path(part):
                    return False, f"Unsafe path: {part}"

        return True, None

    def create_context(self, command: str) -> CommandContext:
        """
        Create execution context for a command.

        Args:
            command: The command to execute.

        Returns:
            CommandContext with execution details.
        """
        return CommandContext(
            command=self.platform_mgr.convert_command(command),
            cwd=os.getcwd(),
            env=os.environ.copy(),
            user=os.getlogin(),
            timestamp=datetime.now(),
            platform=self.platform_mgr.system,
        )

    def execute_shell_command(self, command: str) -> Tuple[int, Optional[str], Optional[str]]:
        """
        Execute a shell command safely and return its results.

        Args:
            command: The shell command to execute.

        Returns:
            Tuple of (return_code, stdout, stderr).
            stdout and stderr are None if capture_output=False.

        Raises:
            SandboxExecutionError: If the command fails validation or execution fails.
        """
        try:
            # Validate command
            is_safe, error = self.validate_command(command)
            if not is_safe:
                raise SandboxExecutionError(f"Unsafe command: {error}")

            # Create execution context
            context = self.create_context(command)

            # Log execution
            logger.info(
                "Executing command: %s (user=%s, cwd=%s, platform=%s)",
                command,
                context.user,
                context.cwd,
                context.platform,
            )

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.RESOURCE_LIMITS["MAX_CPU_TIME"],
                cwd=context.cwd,
                env=context.env,
            )

            # Log success/failure
            if result.returncode == 0:
                logger.info(
                    "Command completed successfully: %s (returncode=%d)",
                    command,
                    result.returncode,
                )
            else:
                logger.error(
                    "Command failed with code %d: %s\nError: %s",
                    result.returncode,
                    command,
                    result.stderr,
                )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {self.RESOURCE_LIMITS['MAX_CPU_TIME']} seconds"
            logger.error("%s: %s", error_msg, command)
            raise SandboxExecutionError(error_msg) from e

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            logger.error("%s: %s", error_msg, command)
            raise SandboxExecutionError(error_msg) from e


# Global sandbox instance
sandbox = Sandbox()
