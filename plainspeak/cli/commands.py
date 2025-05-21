"""
Command definitions for the PlainSpeak CLI.

This module provides the command definitions for the PlainSpeak CLI.
"""

import subprocess
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ..context import session_context
from ..learning import learning_store
from .compat import CommandParser

app = typer.Typer(
    name="plainspeak",
    help="Turn natural language into shell commands.",
    add_completion=False,  # We'll add this later
)

# Create console for rich output
console = Console()


@app.command()
def translate(
    text: str = typer.Argument(..., help="Command description in natural language"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute the translated command"),
):
    """Translate natural language into a shell command."""
    # Check for empty input first
    if not text.strip():
        console.print("Error: Empty input", style="red")
        raise typer.Exit(1)

    # Get context information for learning store
    session_context.get_system_info()
    session_context.get_environment_info()

    # Create parser
    parser = CommandParser(llm=session_context.llm_interface)

    # Parse natural language to command
    success, result = parser.parse(text)

    # Add to learning store
    command_id = learning_store.add_command(
        natural_text=text,
        generated_command=result,
        executed=False,  # Will be updated if executed
        success=success,
    )

    if success:
        syntax = Syntax(result, "bash", theme="monokai")
        console.print(Panel(syntax, title="Generated Command", border_style="green"))

        # Add positive feedback
        learning_store.add_feedback(command_id, "approve")

        if execute:
            console.print("\nExecuting command:", style="yellow")
            try:
                process = subprocess.run(result, shell=True, check=False, capture_output=True, text=True)

                # Display output
                if process.stdout:
                    console.print(process.stdout, end="")
                if process.stderr:
                    console.print(process.stderr, end="")

                # Update execution status
                success = process.returncode == 0
                learning_store.update_command_execution(command_id, True, success)

                if success:
                    console.print("Command executed successfully", style="green")
                else:
                    console.print(f"Command failed with exit code {process.returncode}", style="red")

                # Add to history
                session_context.add_to_history(text, result, success)

                if not success:
                    raise typer.Exit(1)

            except Exception as e:
                console.print(f"Error executing command: {e}", style="red")
                learning_store.update_command_execution(command_id, True, False, str(e))
                session_context.add_to_history(text, result, False)
                raise typer.Exit(1)
    else:
        # Format the error message for better readability
        if "LLM interface not properly configured" in result or "No LLM provider configured" in result:
            # Special handling for configuration errors
            console.print(
                Panel(
                    f"{result}\n\n[bold]Troubleshooting:[/bold]\n"
                    f"1. Run [cyan]plainspeak config --download-model[/cyan] to set up the model\n"
                    f"2. Run [cyan]plainspeak config[/cyan] to view your current configuration\n"
                    f"3. For remote providers like OpenAI, run\n"
                    f"  [cyan]plainspeak config --provider openai --api-key YOUR_KEY[/cyan]",
                    title="Configuration Error",
                    border_style="red",
                )
            )
        else:
            # General error handling
            console.print(Panel(result, title="Error", border_style="red"))

        learning_store.add_feedback(command_id, "reject", "Command generation failed")
        raise typer.Exit(1)


@app.command()
def shell():
    """Start an interactive shell for natural language command translation."""
    from . import PlainSpeakShell

    try:
        PlainSpeakShell().cmdloop()
    except KeyboardInterrupt:
        console.print("\nExiting shell...", style="yellow")
        # Save context before exiting
        session_context.save_context()
        sys.exit(0)
    except Exception as e:
        console.print(f"\nError in shell: {e}", style="red")
        # Try to save context even on error
        try:
            session_context.save_context()
        except Exception:
            pass
        sys.exit(1)
