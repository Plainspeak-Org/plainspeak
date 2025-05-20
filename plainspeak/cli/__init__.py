"""
Command Line Interface for PlainSpeak.

This module provides both a command-line interface for one-off command generation
and an interactive REPL mode for continuous command translation.
"""

import shlex
import subprocess
import sys
from typing import Optional, Tuple

import typer
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ..context import session_context
from ..core.llm import LLMInterface
from ..core.parser import NaturalLanguageParser
from ..learning import learning_store


class CommandParser:
    """
    Parser for natural language commands.

    This is a compatibility class for tests that expect a CommandParser class.
    It wraps the NaturalLanguageParser class.
    """

    def __init__(self, llm=None):
        """Initialize the command parser."""
        self.llm = llm or LLMInterface()
        self.parser = NaturalLanguageParser(llm=self.llm, i18n=session_context.i18n)

    def parse_to_command(self, text: str) -> Tuple[bool, str]:
        """
        Parse natural language text to a shell command.

        Args:
            text: The natural language text to parse.

        Returns:
            Tuple of (success, command or error message).
        """
        if not text:
            return False, "Empty input"

        try:
            # self.parser is NaturalLanguageParser, its 'parse' method returns Union[Tuple[bool, str], Dict[str, Any]]
            result_from_nlp = self.parser.parse(text)

            if isinstance(result_from_nlp, dict):
                parsed_ast = result_from_nlp
                if parsed_ast.get("verb"):
                    # Basic command generation
                    # Ensure args are handled correctly, e.g., boolean flags without values
                    command_parts = [parsed_ast["verb"]]
                    args_dict = parsed_ast.get("args", {})
                    for k, v in args_dict.items():
                        if isinstance(v, bool):
                            if v is True:  # Add flag if true
                                command_parts.append(f"--{k}")
                        else:  # Add option with value
                            command_parts.append(f"--{k}")
                            command_parts.append(shlex.quote(str(v)))  # Quote values
                    command = " ".join(command_parts)
                    return True, command
                else:
                    # This case implies the dict was returned but had no 'verb'
                    # which is an issue with the LLM output or its processing.
                    error_msg = parsed_ast.get("error", "Could not parse command (missing verb in AST)")
                    return False, error_msg
            elif (
                isinstance(result_from_nlp, tuple)
                and len(result_from_nlp) == 2
                and isinstance(result_from_nlp[0], bool)
            ):
                # This is the (success: bool, message: str) tuple, likely from an error or test mode
                return result_from_nlp[0], result_from_nlp[1]
            else:
                # Unexpected return type from NaturalLanguageParser.parse
                return False, "Unexpected result from natural language parser"

        except Exception as e:
            # Log the exception for debugging
            # import logging
            # logging.exception("Error in CommandParser.parse_to_command")
            return False, f"Error parsing command: {e}"


# Import compatibility classes for tests

app = typer.Typer(
    name="plainspeak",
    help="Turn natural language into shell commands.",
    add_completion=False,  # We'll add this later
)

# Create console for rich output
console = Console()


@app.command()
def translate(
    text: str = typer.Argument(..., help="Natural language command to translate"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute the translated command"),
):
    """Translate natural language to a shell command."""
    if not text:
        console.print("Error: Empty input", style="red")
        raise typer.Exit(1)

    # Create a command parser
    parser = CommandParser()

    # Parse the command
    success, command = parser.parse_to_command(text)

    if success:
        syntax = Syntax(command, "bash", theme="monokai")
        console.print(Panel(syntax, title="Generated Command", border_style="green"))

        if execute:
            try:
                process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
                success = process.returncode == 0

                if process.stdout:
                    console.print(process.stdout, end="")
                if process.stderr:
                    console.print(process.stderr, end="")

                if success:
                    console.print("Command executed successfully", style="green")
                else:
                    console.print(f"Command failed with exit code {process.returncode}", style="red")
                    raise typer.Exit(1)
            except Exception as e:
                console.print(f"Error executing command: {e}", style="red")
                raise typer.Exit(1)
    else:
        console.print(Panel(command, title="Error", border_style="red"))
        raise typer.Exit(1)


@app.command()
def shell():
    """Start an interactive shell for translating natural language to commands."""
    shell = PlainSpeakShell()
    shell.cmdloop()


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
        self.parser = CommandParser(llm=session_context.llm_interface)
        # Remove some default cmd2 commands we don't need
        self.do_edit = None
        self.do_shortcuts = None
        self.do_shell = None
        self.do_macro = None
        self.do_alias = None
        self.do_run_script = None
        self.do_run_pyscript = None

    translate_parser = Cmd2ArgumentParser()
    translate_parser.add_argument("text", nargs="+", help="The command description in natural language")
    translate_parser.add_argument("-e", "--execute", action="store_true", help="Execute the translated command")

    @with_argparser(translate_parser)
    def do_translate(self, args):
        """Translate natural language to a shell command."""
        text = " ".join(args.text).strip()
        if not text:
            console.print("Error: Empty input", style="red")
            return

        # Get context information for learning store
        system_info = session_context.get_system_info()
        environment_info = session_context.get_environment_info()

        # Parse using CommandParser
        success, result = self.parser.parse_to_command(text)

        # Add to learning store
        command_id = learning_store.add_command(
            natural_text=text,
            generated_command=result,
            executed=False,
            system_info=system_info,
            environment_info=environment_info,
        )

        if success:
            syntax = Syntax(result, "bash", theme="monokai")
            console.print(Panel(syntax, title="Generated Command", border_style="green"))

            learning_store.add_feedback(command_id, "approve")

            if args.execute:
                success = self.do_execute(result, original_text=text)
                learning_store.update_command_execution(command_id, True, success)
        else:
            console.print(Panel(result, title="Error", border_style="red"))
            learning_store.add_feedback(command_id, "reject", "Command generation failed")

    def do_execute(self, command: str, original_text: Optional[str] = None) -> bool:
        """Execute a command and return success status."""
        command = command.strip()
        if not command:
            console.print("Error: Empty input", style="red")
            return False

        try:
            process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
            success = process.returncode == 0

            if process.stdout:
                console.print(process.stdout, end="")
            if process.stderr:
                console.print(process.stderr, end="")

            if original_text:
                session_context.add_to_history(original_text, command, success)

            if success:
                console.print("Command executed successfully", style="green")
            else:
                console.print(f"Command failed with exit code {process.returncode}", style="red")
                if process.stderr:
                    console.print(process.stderr, style="red")

            return success

        except Exception as e:
            console.print(f"Error executing command: {e}", style="red")
            if original_text:
                session_context.add_to_history(original_text, command, False)
            return False

    def do_exit(self, _):
        """Exit the shell."""
        session_context.save_context()
        return True

    def default(self, statement):
        """Handle unknown commands as natural language input."""
        text = getattr(statement, "raw", str(statement)).strip()
        if text:
            return self.onecmd(f"translate {text}")
        return False


def main():
    """Entry point for the CLI."""
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


__all__ = ["PlainSpeakShell", "app", "main"]
