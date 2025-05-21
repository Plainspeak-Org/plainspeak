"""
Command Line Interface for PlainSpeak.

This module provides both a command-line interface for one-off command generation
and an interactive REPL mode for continuous command translation.
"""

import sys

import typer
from rich.console import Console

from ..context import session_context
from .config_cmd import config_command
from .parser import CommandParser
from .plugins_cmd import plugins_command
from .shell import PlainSpeakShell
from .translate_cmd import translate_command
from .utils import initialize_context

# Create the Typer app
app = typer.Typer(
    name="plainspeak",
    help="Turn natural language into shell commands.",
    add_completion=False,  # We'll add this later
)

# Create console for rich output
console = Console()

# Register commands
app.command(name="translate")(translate_command)
app.command(name="config")(config_command)
app.command(name="plugins")(plugins_command)


# Add a callback to handle direct commands without 'translate' verb
@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    text: str = typer.Argument(None, help="Natural language command to translate"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute the translated command"),
):
    """Process natural language without requiring the 'translate' verb."""
    if ctx.invoked_subcommand:
        return  # Let the subcommand handle it

    if text:
        # Explicitly set execute=False unless the user specified -e/--execute flag
        translate_command(text, execute=execute)


@app.command()
def shell():
    """Start an interactive shell for translating natural language to commands."""
    shell = PlainSpeakShell()
    shell.cmdloop()


def main():
    """Entry point for the CLI."""
    # Initialize context before running commands
    initialize_context()

    try:
        app()
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        try:
            session_context.save_context()
        except Exception:
            pass
        sys.exit(1)
    finally:
        session_context.save_context()


__all__ = ["CommandParser", "PlainSpeakShell", "app", "main"]
