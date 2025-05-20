"""
Command Line Interface for PlainSpeak.

This module provides both a command-line interface for one-off command generation
and an interactive REPL mode for continuous command translation.
"""

import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from plainspeak.config import ensure_default_config_exists, load_config
from plainspeak.core.i18n import I18n
from plainspeak.core.llm import LLMInterface, get_llm_interface
from plainspeak.core.parser import NaturalLanguageParser

from .context import session_context
from .learning import learning_store
from .plugins.manager import plugin_manager

# Create the Typer app
app = typer.Typer(
    name="plainspeak",
    help="Turn natural language into shell commands.",
    add_completion=False,  # We'll add this later
)

# Create console for rich output
console = Console()


# --- Module-level initialization helper ---
def _initialize_context():
    """Ensures config is loaded and session_context components are initialized."""
    ensure_default_config_exists()  # Ensure a default config is present
    current_config = load_config()  # Load the most up-to-date config

    # Update the global app_config if it was imported and needs to be refreshed
    # This line assumes direct modification of the imported global_app_config is intended
    # If global_app_config is just for type hinting, this might not be necessary,
    # but if other modules rely on plainspeak.config.app_config being the *latest*, it is.
    # For now, we primarily care that get_llm_interface gets the right config.
    # plainspeak.config.app_config = current_config # Potentially update global module instance

    if not session_context.llm_interface or not isinstance(session_context.llm_interface, LLMInterface):
        session_context.llm_interface = get_llm_interface(current_config)

    if not session_context.i18n or not isinstance(session_context.i18n, I18n):
        # Assuming I18n() default is okay or it uses global_app_config internally if needed.
        # If I18n needs specific config: session_context.i18n = I18n(config=current_config)
        session_context.i18n = I18n()

    # Optionally, store the loaded config in session_context if needed elsewhere
    # session_context.config = current_config


# Call initialization immediately after definition
_initialize_context()
# --- End module-level initialization ---


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

        # Ensure llm_interface and i18n are initialized before parser
        if (
            not session_context.llm_interface
            or not isinstance(session_context.llm_interface, LLMInterface)
            or not session_context.i18n
            or not isinstance(session_context.i18n, I18n)
        ):
            _initialize_context()  # Fallback initialization

        if not session_context.llm_interface or not isinstance(session_context.llm_interface, LLMInterface):
            # If still not initialized, something is critically wrong
            console.print("Critical Error: LLM Interface could not be initialized for PlainSpeakShell.", style="red")
            # Optionally raise an error or prevent shell from starting
            # For now, we'll let it proceed, but parser init will likely fail or use a None llm.
            # raise RuntimeError("LLM Interface could not be initialized for PlainSpeakShell.")
            pass  # Allow to proceed, NaturalLanguageParser might handle None llm if designed for it

        self.parser = NaturalLanguageParser(llm=session_context.llm_interface, i18n=session_context.i18n)
        # Remove some default cmd2 commands we don't need by setting them to None
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

        # Use NaturalLanguageParser.parse and then convert AST to command string
        parsed_ast = self.parser.parse(text)  # Use parse method

        # Placeholder AST to string conversion (likely needs refinement)
        if parsed_ast.get("verb"):
            # This is a very basic conversion. A more sophisticated AST to command string
            # rendering, possibly involving the Commander or a dedicated template engine,
            # would be needed for robust functionality.
            # For now, assume verb is the command and args are simple key-value pairs.
            verb = parsed_ast["verb"]
            args_dict = parsed_ast.get("args", {})

            # Attempt to reconstruct a command string. This is highly dependent on
            # how plugins and commands are structured.
            # If a plugin manager and commander are involved, they should handle this.
            # For now, a simple reconstruction:
            command_parts = [verb]
            for k, v in args_dict.items():
                if isinstance(v, bool) and v is True:  # Handle boolean flags
                    command_parts.append(f"--{k}")
                elif v is not None:  # Add other args
                    command_parts.append(f"--{k}")
                    command_parts.append(str(v))

            result = " ".join(command_parts)
            success = True
        else:
            result = "Error: Could not parse command from natural language."
            success = False

        # Add to learning store
        command_id = learning_store.add_command(
            natural_text=text,
            generated_command=result,
            executed=False,  # Will be updated if executed
            system_info=system_info,
            environment_info=environment_info,
        )

        if success:
            syntax = Syntax(result, "bash", theme="monokai")
            panel = Panel(syntax, title="Generated Command", border_style="green")
            console.print(panel)

            # Add positive feedback
            learning_store.add_feedback(command_id, "approve")

            if args.execute and result.strip():  # Only execute non-empty commands
                execution_success = self.do_execute(result, original_text=text)
                # Update execution status in learning store
                learning_store.update_command_execution(command_id, True, execution_success)
        else:
            panel = Panel(result, title="Error", border_style="red")
            console.print(panel)

            # Add negative feedback
            learning_store.add_feedback(command_id, "reject", "Command generation failed")

    def do_execute(self, command, original_text=None):
        """Execute a generated command."""
        command = command.strip()
        if not command:
            console.print("Error: Empty input", style="red")
            return

        try:
            # Using shell=True for now to allow complex commands, but this has security implications
            # if the command is not properly sanitized.
            process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)

            # Display output
            if process.stdout:
                console.print(process.stdout, end="")
            if process.stderr:
                console.print(process.stderr, end="")

            # Update session context with execution result
            success = process.returncode == 0

            # If we have the original text, update the history with execution result
            if original_text and isinstance(original_text, str):
                # This will overwrite the previous entry with the same command but updated success status
                session_context.add_to_history(original_text, command, success)

            # Display success/failure message
            if success:
                console.print("Command executed successfully", style="green")
            else:
                console.print(f"Command failed with exit code {process.returncode}", style="red")
                if process.stderr:
                    console.print(process.stderr, style="red")

            return success

        except subprocess.SubprocessError as e:
            console.print(f"Error executing command: {e}", style="red")
            if original_text:
                session_context.add_to_history(original_text, command, False)
            return False
        except FileNotFoundError:
            console.print(f"Error: Command not found: {command.split()[0]}", style="red")
            if original_text:
                session_context.add_to_history(original_text, command, False)
            return False
        except Exception as e:
            console.print(f"Error executing command: {e}", style="red")
            if original_text:
                session_context.add_to_history(original_text, command, False)
            return False

    def default(self, statement):
        """Handle unknown commands as natural language input."""
        # Get the original input text from the statement object
        text = getattr(statement, "raw", str(statement)).strip()
        if text:
            # Pass the entire input to translate
            return self.onecmd(f"translate {text}")
        return False

    def do_history(self, args):
        """Show command history."""
        # Get history from session context
        history = session_context.get_history(limit=20)

        if not history:
            console.print("No command history found.", style="yellow")
            return

        console.print("Command History:", style="bold")
        for i, entry in enumerate(history, 1):
            # Format timestamp
            timestamp = entry.get("timestamp", "").split("T")[0]  # Just get the date part

            # Format success/failure
            success = entry.get("success", False)
            status = "[green]✓[/green]" if success else "[red]✗[/red]"

            # Format the entry
            console.print(
                f"{i}. {status} [{timestamp}] [bold]{entry.get('natural_text', '')}[/bold]",
                highlight=False,
            )
            console.print(f"   → {entry.get('command', '')}", style="dim")

    def do_context(self, args):
        """Show current session context."""
        context = session_context.get_full_context()

        # System info
        console.print("System Information:", style="bold")
        for key, value in context.get("system", {}).items():
            console.print(f"  {key}: {value}")

        # Environment info
        console.print("\nEnvironment:", style="bold")
        for key, value in context.get("environment", {}).items():
            console.print(f"  {key}: {value}")

        # Session variables
        console.print("\nSession Variables:", style="bold")
        session_vars = context.get("session_vars", {})
        if session_vars:
            for key, value in session_vars.items():
                console.print(f"  {key}: {value}")
        else:
            console.print("  No session variables set.", style="dim")

        # History size
        console.print(f"\nCommand History: {context.get('history_size', 0)} entries", style="bold")

    def do_learning(self, args):
        """Show learning store data."""
        try:
            # Get command history from learning store
            history_df = learning_store.get_command_history(limit=10)

            if history_df.empty:
                console.print("No command history found in learning store.", style="yellow")
                return

            console.print("Learning Store Command History (last 10 entries):", style="bold")

            # Format and display the history
            for _, row in history_df.iterrows():
                # Format timestamp
                timestamp = row.get("timestamp", "").split("T")[0]  # Just get the date part

                # Format success/failure
                success = row.get("success")
                if success is None:
                    status = "[yellow]?[/yellow]"  # Not executed
                elif success:
                    status = "[green]✓[/green]"  # Success
                else:
                    status = "[red]✗[/red]"  # Failure

                # Format the entry
                console.print(
                    f"{row.get('id', '?')}. {status} [{timestamp}] [bold]{row.get('natural_text', '')}[/bold]",
                    highlight=False,
                )

                # Show the command
                if row.get("edited", False):
                    console.print(
                        f"   → [original] {row.get('generated_command', '')}",
                        style="dim",
                    )
                    console.print(
                        f"   → [edited] {row.get('edited_command', '')}",
                        style="green dim",
                    )
                else:
                    console.print(f"   → {row.get('generated_command', '')}", style="dim")

            # Show stats
            console.print("\nLearning Statistics:", style="bold")

            # Count successful commands
            success_count = len(history_df[history_df["success"] == True])
            total_executed = len(history_df[history_df["executed"] == True])
            if total_executed > 0:
                success_rate = (success_count / total_executed) * 100
                console.print(f"  Success Rate: {success_rate:.1f}% ({success_count}/{total_executed})")

            # Count edited commands
            edited_count = len(history_df[history_df["edited"] == True])
            console.print(f"  Edited Commands: {edited_count}/{len(history_df)}")

        except Exception as e:
            console.print(f"Error accessing learning store: {e}", style="red")

    export_parser = Cmd2ArgumentParser()
    export_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: ./plainspeak_training_data.jsonl)",
        default="./plainspeak_training_data.jsonl",
    )

    @with_argparser(export_parser)
    def do_export(self, args):
        """Export training data from the learning store."""
        try:
            output_path = Path(args.output)

            console.print(f"Exporting training data to {output_path}...", style="yellow")

            # Export the data
            count = learning_store.export_training_data(output_path)

            if count > 0:
                console.print(
                    f"Successfully exported {count} training examples to {output_path}",
                    style="green",
                )
            else:
                console.print("No training examples found to export.", style="yellow")

        except Exception as e:
            console.print(f"Error exporting training data: {e}", style="red")

    def do_plugins(self, args):
        """List available plugins and their verbs."""
        plugins = plugin_manager.get_all_plugins()

        if not plugins:
            console.print("No plugins found.", style="yellow")
            return

        console.print("Available Plugins:", style="bold")

        for name, plugin in plugins.items():
            console.print(f"\n[bold]{name}[/bold]: {plugin.description}")

            # Get verbs for this plugin
            verbs = plugin.get_verbs()
            if verbs:
                console.print("  Supported verbs:", style="dim")
                # Group verbs in rows of 5 for better display
                verb_groups = [verbs[i : i + 5] for i in range(0, len(verbs), 5)]
                for group in verb_groups:
                    console.print("  " + ", ".join(group), style="green")

    def do_exit(self, _):
        """Exit the shell."""
        # Save context before exiting
        session_context.save_context()
        return True


@app.command()
def translate(
    text: str = typer.Argument(..., help="Command description in natural language"),
    execute: bool = typer.Option(False, "--execute", "-e", help="Execute the translated command"),
):
    """Translate natural language into a shell command."""
    if not text.strip():
        console.print("Error: Empty input", style="red")
        raise typer.Exit(1)

    # Ensure llm_interface and i18n are initialized before parser
    if (
        not session_context.llm_interface
        or not isinstance(session_context.llm_interface, LLMInterface)
        or not session_context.i18n
        or not isinstance(session_context.i18n, I18n)
    ):
        _initialize_context()  # Fallback initialization

    if not session_context.llm_interface or not isinstance(session_context.llm_interface, LLMInterface):
        console.print("Critical Error: LLM Interface could not be initialized for translate command.", style="red")
        raise typer.Exit(code=1)

    system_info = session_context.get_system_info()
    environment_info = session_context.get_environment_info()

    parser = NaturalLanguageParser(llm=session_context.llm_interface, i18n=session_context.i18n)

    result_from_nlp = parser.parse(text)

    final_command_str: Optional[str] = None
    success: bool = False

    if isinstance(result_from_nlp, dict):
        parsed_dict = result_from_nlp
        if parsed_dict.get("verb"):
            command_parts = [parsed_dict["verb"]]
            args_dict = parsed_dict.get("args", {})
            for k, v_raw in args_dict.items():
                if isinstance(v_raw, bool):
                    if v_raw is True:
                        command_parts.append(f"--{k}")
                else:
                    command_parts.append(f"--{k}")
                    command_parts.append(shlex.quote(str(v_raw)))
            final_command_str = " ".join(command_parts)
            success = True
        else:
            final_command_str = parsed_dict.get("error", "Error: Could not parse command (missing verb).")
            success = False
    elif isinstance(result_from_nlp, tuple) and len(result_from_nlp) == 2 and isinstance(result_from_nlp[0], bool):
        success, final_command_str = result_from_nlp
    else:
        final_command_str = "Error: Unexpected result from parser."
        success = False

    # Add to learning store - ensure 'result' for learning store is the command string or error message
    command_id = learning_store.add_command(
        natural_text=text,
        generated_command=final_command_str if final_command_str is not None else "Parsing failed",
        executed=False,
        success=success,
        system_info=system_info,
        environment_info=environment_info,
    )

    if success and final_command_str is not None:
        syntax = Syntax(final_command_str, "bash", theme="monokai")
        console.print(Panel(syntax, title="Generated Command", border_style="green"))

        # Add positive feedback before execution attempt
        learning_store.add_feedback(command_id, "approve")

        if execute:
            console.print("\nExecuting command:", style="yellow")
            try:
                process = subprocess.run(final_command_str, shell=True, check=False, capture_output=True, text=True)
                execution_success = process.returncode == 0

                # Display output
                if process.stdout:
                    console.print(process.stdout, end="")
                if process.stderr:
                    console.print(
                        Panel(process.stderr, title="Command Error Output", border_style="orange_red1"), end=""
                    )

                # Update session context with execution result
                session_context.add_to_history(text, final_command_str, execution_success)

                # Update learning store with execution result
                learning_store.update_command_execution(command_id, True, execution_success)

                if execution_success:
                    console.print("\nCommand executed successfully.", style="green")
                else:
                    console.print(f"\nCommand failed with exit code {process.returncode}.", style="red")
                    # No typer.Exit here, allow flow to complete for learning store updates if any

            except subprocess.SubprocessError as e:
                console.print(f"Error executing command: {e}", style="red")
                session_context.add_to_history(text, final_command_str, False)
                learning_store.update_command_execution(command_id, True, False)
                raise typer.Exit(1)
            except FileNotFoundError:
                console.print(f"Error: Command not found: {final_command_str.split()[0]}", style="red")
                session_context.add_to_history(text, final_command_str, False)
                learning_store.update_command_execution(command_id, True, False)
                raise typer.Exit(1)
            except Exception as e:  # General exception
                console.print(f"Error executing command: {e}", style="red")
                session_context.add_to_history(text, final_command_str, False)
                learning_store.update_command_execution(command_id, True, False)
                raise typer.Exit(1)
    else:
        console.print(
            Panel(
                final_command_str if final_command_str is not None else "Unknown parsing error",
                title="Error",
                border_style="red",
            )
        )
        # Add negative feedback if parsing failed or produced no command
        if command_id:
            learning_store.add_feedback(command_id, "reject", final_command_str or "Command generation failed")
        raise typer.Exit(1)


@app.command()
def plugins():
    """List available plugins and their verbs."""
    plugins = plugin_manager.get_all_plugins()

    if not plugins:
        console.print("No plugins found.", style="yellow")
        return

    console.print("Available Plugins:", style="bold")

    for name, plugin in plugins.items():
        console.print(f"\n[bold]{name}[/bold]: {plugin.description}")

        # Get verbs for this plugin
        verbs = plugin.get_verbs()
        if verbs:
            console.print("  Supported verbs:", style="dim")
            # Group verbs in rows of 5 for better display
            verb_groups = [verbs[i : i + 5] for i in range(0, len(verbs), 5)]
            for group in verb_groups:
                console.print("  " + ", ".join(group), style="green")


@app.command()
def shell():
    """Start an interactive shell for natural language command translation."""
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


def main():
    """Entry point for the CLI."""
    # Ensure context is initialized, as _initialize_context() might have been called
    # when the module was first imported, but this guarantees it before app() runs,
    # especially if main can be invoked in ways that bypass full module reload.
    if (
        not session_context.llm_interface
        or not isinstance(session_context.llm_interface, LLMInterface)
        or not session_context.i18n
        or not isinstance(session_context.i18n, I18n)
    ):
        _initialize_context()

    try:
        app()
    except Exception as e:
        console.print(f"Error: {e}", style="red")
        # Try to save context even on error
        try:
            session_context.save_context()
        except Exception:
            pass  # Silently ignore if context saving fails during error handling
        sys.exit(1)
    finally:
        # Save context on normal exit or if an unhandled exception occurs before try/except in main
        session_context.save_context()


if __name__ == "__main__":
    main()
