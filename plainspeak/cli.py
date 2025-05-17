"""
Command Line Interface for PlainSpeak.

This module provides both a command-line interface for one-off command generation
and an interactive REPL mode for continuous command translation.
"""
import sys
from typing import Optional
import typer
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .parser import CommandParser
from .llm_interface import LLMInterface

# Create the Typer app
app = typer.Typer(
    name="plainspeak",
    help="Turn natural language into shell commands.",
    add_completion=False,  # We'll add this later
)

# Create console for rich output
console = Console()

class PlainSpeakShell(Cmd):
    """
    Interactive shell for translating natural language to commands.
    """
    intro = """Welcome to PlainSpeak Shell!
Type your commands in plain English, and they will be translated to shell commands.
Type 'help' for a list of commands, or 'exit' to quit.\n"""
    prompt = "🗣️ > "

    def __init__(self):
        """Initialize the PlainSpeak shell."""
        super().__init__(allow_cli_args=False)
        self.parser = CommandParser()
        # Remove some default cmd2 commands we don't need by setting them to None
        self.do_edit = None
        self.do_shortcuts = None
        self.do_shell = None
        self.do_macro = None
        self.do_alias = None
        self.do_run_script = None
        self.do_run_pyscript = None

    translate_parser = Cmd2ArgumentParser()
    translate_parser.add_argument(
        'text',
        nargs='+',
        help='The command description in natural language'
    )
    translate_parser.add_argument(
        '-e', '--execute',
        action='store_true',
        help='Execute the translated command'
    )

    @with_argparser(translate_parser)
    def do_translate(self, args):
        """Translate natural language to a shell command."""
        text = ' '.join(args.text).strip()
        if not text:
            console.print("Error: Empty input", style="red")
            return

        success, result = self.parser.parse_to_command(text)
        
        if success:
            syntax = Syntax(result, "bash", theme="monokai")
            panel = Panel(syntax, title="Generated Command", border_style="green")
            console.print(panel)
            if args.execute and result.strip():  # Only execute non-empty commands
                self.do_execute(result)
        else:
            panel = Panel(result, title="Error", border_style="red")
            console.print(panel)

    def do_execute(self, command):
        """Execute a generated command."""
        command = command.strip()
        if not command:
            console.print("Error: Empty input", style="red")
            return

        # Use subprocess for better control and security
        import subprocess
        try:
            # Using shell=True for now to allow complex commands, but this has security implications
            # if the command is not properly sanitized.
            process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
            if process.stdout:
                console.print(process.stdout, end="")
            if process.stderr:
                console.print(process.stderr, end="")
            if process.returncode == 0:
                console.print("Command executed successfully", style="green")
            else:
                console.print(f"Command failed with exit code {process.returncode}", style="red")
                if process.stderr:
                    console.print(process.stderr, style="red")
        except subprocess.SubprocessError as e:
            console.print(f"Error executing command: {e}", style="red")
        except FileNotFoundError:
            console.print(f"Error: Command not found: {command.split()[0]}", style="red")
        except Exception as e:
            console.print(f"Error executing command: {e}", style="red")

    def default(self, statement):
        """Handle unknown commands as natural language input."""
        # Get the original input text from the statement object
        text = getattr(statement, 'raw', str(statement)).strip()
        if text:
            # Pass the entire input to translate
            return self.onecmd(f'translate {text}')
        return False

    def do_exit(self, _):
        """Exit the shell."""
        return True

@app.command()
def translate(
    text: str = typer.Argument(..., help="Command description in natural language"),
    execute: bool = typer.Option(
        False,
        "--execute", "-e",
        help="Execute the translated command"
    ),
):
    """Translate natural language into a shell command."""
    # Check for empty input first
    if not text.strip():
        console.print("Error: Empty input", style="red")
        raise typer.Exit(1)

    # CommandParser will use LLMInterface, which now uses app_config by default
    parser = CommandParser()
    success, result = parser.parse_to_command(text)
    
    if success:
        syntax = Syntax(result, "bash", theme="monokai")
        console.print(Panel(syntax, title="Generated Command", border_style="green"))
        
        if execute:
            console.print("\nExecuting command:", style="yellow")
            import subprocess
            try:
                process = subprocess.run(
                    result,
                    shell=True,
                    check=False,
                    capture_output=True,
                    text=True
                )
                if process.stdout:
                    console.print(process.stdout, end="")
                if process.stderr:
                    console.print(process.stderr, end="")
                if process.returncode == 0:
                    console.print("Command executed successfully", style="green")
                else:
                    console.print(f"Command failed with exit code {process.returncode}", style="red")
                    if process.stderr:
                        console.print(process.stderr, style="red")
                    raise typer.Exit(1)
            except subprocess.SubprocessError as e:
                console.print(f"Error executing command: {e}", style="red")
                raise typer.Exit(1)
            except FileNotFoundError:
                console.print(f"Error: Command not found: {result.split()[0]}", style="red")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"Error executing command: {e}", style="red")
                raise typer.Exit(1)
    else:
        console.print(Panel(result, title="Error", border_style="red"))
        raise typer.Exit(1)

@app.command()
def shell():
    """Start an interactive shell for natural language command translation."""
    try:
        PlainSpeakShell().cmdloop()
    except KeyboardInterrupt:
        console.print("\nExiting shell...", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\nError in shell: {e}", style="red")
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
