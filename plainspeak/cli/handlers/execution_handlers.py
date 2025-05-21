"""
Command handlers for executing commands.

This module provides the command handlers for executing commands in the PlainSpeak shell.
"""

from typing import Optional

from rich.console import Console

from ...context import session_context
from ..shell_utils import display_execution_result, execute_command

# Create console for rich output
console = Console()


def handle_execute(shell, command: str, original_text: Optional[str] = None) -> bool:
    """
    Execute a command and display the results.

    Args:
        shell: The shell instance
        command: The command to execute
        original_text: The original natural language text (if available)

    Returns:
        Boolean indicating if execution was successful
    """
    command = command.strip()
    if not command:
        console.print("Error: Empty input", style="red")
        return False

    console.print("\nExecuting command:", style="yellow")

    success, stdout, stderr = execute_command(command)

    # Display output
    display_execution_result(success, stdout, stderr)

    # If we have the original text, update the history with execution result
    if original_text and isinstance(original_text, str):
        # This will overwrite the previous entry with the same command but updated success status
        session_context.add_to_history(original_text, command, success)

    return success


def handle_exec(shell, args):
    """
    Handle the exec command.

    Args:
        shell: The shell instance
        args: Command arguments parsed by the exec_parser
    """
    # Join the command arguments back into a single string
    command = " ".join(args.command).strip()
    if not command:
        console.print("Error: Empty command", style="red")
        return

    console.print(f"Executing: {command}", style="yellow")
    handle_execute(shell, command)


def handle_bang(shell, args):
    """
    Handle the ! (bang) command.

    Args:
        shell: The shell instance
        args: Raw command string
    """
    if not args.strip():
        console.print("Error: Empty command", style="red")
        return

    # Don't try to parse with exec_parser which will break on complex shell commands
    # Just pass the raw string directly to handle_execute
    console.print(f"Executing: {args}", style="yellow")
    return handle_execute(shell, args)
