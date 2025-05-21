"""
Utility functions for the PlainSpeak Shell.

This module provides helper functions used by the PlainSpeak interactive shell.
"""

import subprocess
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .utils import copy_to_clipboard

# Create console for rich output
console = Console()


def display_command(command: str) -> None:
    """
    Display a generated command in a styled panel.

    Args:
        command: The command to display
    """
    syntax = Syntax(command, "bash", theme="monokai")
    panel = Panel(syntax, title="Generated Command", border_style="green")
    console.print(panel)

    # Try to copy to clipboard
    if copy_to_clipboard(command):
        console.print("[bright_green]✓ Command copied to clipboard[/bright_green]")


def display_error(error_message: str, title: str = "Error") -> None:
    """
    Display an error message in a styled panel.

    Args:
        error_message: The error message to display
        title: The panel title (default: "Error")
    """
    panel = Panel(error_message, title=title, border_style="red")
    console.print(panel)


def execute_command(command: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Execute a shell command and return the result.

    Args:
        command: The command to execute

    Returns:
        Tuple containing:
        - success: Boolean indicating if execution was successful
        - stdout: Command standard output (or None)
        - stderr: Command standard error (or None)
    """
    command = command.strip()
    if not command:
        console.print("Error: Empty input", style="red")
        return False, None, None

    try:
        # Using shell=True for now to allow complex commands
        process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)

        # Get output
        stdout = process.stdout if process.stdout else None
        stderr = process.stderr if process.stderr else None

        # Determine success
        success = process.returncode == 0

        return success, stdout, stderr

    except Exception as e:
        error_message = str(e)
        return False, None, error_message


def display_execution_result(
    success: bool, stdout: Optional[str], stderr: Optional[str], return_code: int = None
) -> None:
    """
    Display the results of command execution.

    Args:
        success: Whether the command succeeded
        stdout: Command standard output
        stderr: Command standard error
        return_code: Command return code (optional)
    """
    # Display output
    if stdout:
        console.print(stdout, end="")
    if stderr:
        console.print(stderr, end="")

    # Display success/failure message
    if success:
        console.print("Command executed successfully", style="green")
    else:
        if return_code is not None:
            console.print(f"Command failed with exit code {return_code}", style="red")
        else:
            console.print("Command failed", style="red")
