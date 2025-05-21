"""
Command handlers for the PlainSpeak Shell.

This module provides the command handler methods for the PlainSpeak interactive shell.
"""

from pathlib import Path
from typing import Optional

# Remove unused import
from rich.console import Console

from ..context import session_context
from ..core.llm import LocalLLMInterface
from ..learning import learning_store
from ..plugins import plugin_manager
from .shell_utils import display_command, display_error, execute_command, display_execution_result
from .utils import download_model

# Create console for rich output
console = Console()


def handle_translate(shell, args, parser):
    """
    Handle the translate command.
    
    Args:
        shell: The shell instance
        args: The command arguments
        parser: The parser used to parse the command
    """
    text = " ".join(args.text).strip()
    if not text:
        console.print("Error: Empty input", style="red")
        return

    # Get context information for learning store
    system_info = session_context.get_system_info()
    environment_info = session_context.get_environment_info()

    try:
        # Use NaturalLanguageParser.parse and then convert AST to command string
        parsed_ast = shell.parser.parse(text)

        # Basic conversion from AST to command string
        if parsed_ast and parsed_ast.get("verb"):
            # Extract verb and args
            verb = parsed_ast["verb"]
            args_dict = parsed_ast.get("args", {})

            # Reconstruct command string
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
            display_command(result)

            # Add positive feedback
            learning_store.add_feedback(command_id, "approve")

            if args.execute and result.strip():  # Only execute non-empty commands
                handle_execute(shell, result, original_text=text)
                # Update execution status in learning store
                learning_store.update_command_execution(command_id, True, True)  # Assume success for now
            else:
                # Show hints on how to execute the command
                console.print("\nTo execute this command:", style="cyan")
                console.print(f"  Option 1: Type !{result}", style="cyan")
                console.print(f"  Option 2: Type exec {result}", style="cyan")
                console.print(f"  Option 3: Run the same query with -e flag: {text} -e", style="cyan")
        else:
            display_error(result)

            # Add negative feedback
            learning_store.add_feedback(command_id, "reject", "Command generation failed")

    except NotImplementedError:
        # This likely means the LLM is not properly configured
        console.print("Failed to parse intent: No LLM provider configured.", style="red")

        # Display a helpful error panel with troubleshooting information
        error_message = (
            "LLM interface not properly configured. Please run 'plainspeak config --download-model' "
            "to set up the default model, or 'plainspeak config' to view your current configuration.\n\n"
            "Troubleshooting:\n"
            "1. Run plainspeak config --download-model to automatically set up the default model\n"
            "2. Run plainspeak config to view your current configuration\n"
            "3. For remote providers like OpenAI, run\n"
            "   plainspeak config --provider openai --api-key YOUR_KEY"
        )
        display_error(error_message, title="Configuration Error")

        # Prompt for auto-download
        console.print("\nPlainSpeak needs a language model to understand natural language commands.")
        prompt = "Would you like to automatically download the default model now? (y/n): "
        download_choice = input(prompt).lower().strip()

        if download_choice in ("y", "yes"):
            success, model_path, error = download_model(silent=False)
            if success:
                # Reload config and reinitialize the LLM interface
                from ..config import load_config

                current_config = load_config()

                # Reinitialize the LLM interface
                try:
                    # Try to create a LocalLLMInterface directly to verify the model can be loaded
                    local_llm = LocalLLMInterface(current_config)
                    # If we get here, the model was loaded successfully
                    session_context.llm_interface = local_llm
                    shell.parser.llm = session_context.llm_interface
                    console.print("Model loaded successfully! Try your command again.", style="green")
                except Exception as e:
                    console.print(f"Warning: Model downloaded but could not be loaded: {e}", style="yellow")
                    console.print("Using the model may require additional dependencies.", style="yellow")
                    console.print("Try installing one of the following packages:", style="yellow")
                    console.print("  pip install ctransformers", style="cyan")
                    console.print("  pip install ctransformers[cuda] # For NVIDIA GPUs", style="cyan")
                    console.print("  pip install ctransformers[metal] # For Apple Silicon", style="cyan")
            else:
                console.print(
                    "Failed to auto-download model. Please run 'plainspeak config --download-model'.",
                    style="red",
                )
        else:
            console.print(
                "Model download skipped. Please run 'plainspeak config --download-model' to set up the model.",
                style="yellow",
            )

    except Exception as e:
        # Handle any other exceptions
        error_message = str(e).strip()
        if not error_message:
            error_message = f"An unexpected error of type {type(e).__name__} occurred during parsing."

        display_error(error_message)

        # Add to learning store with error
        command_id = learning_store.add_command(
            natural_text=text,
            generated_command="ERROR: " + error_message,
            executed=False,
            system_info=system_info,
            environment_info=environment_info,
        )
        learning_store.add_feedback(command_id, "reject", error_message)


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


def handle_history(shell, args):
    """
    Handle the history command.
    
    Args:
        shell: The shell instance
        args: Command arguments
    """
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


def handle_context(shell, args):
    """
    Handle the context command.
    
    Args:
        shell: The shell instance
        args: Command arguments
    """
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


def handle_learning(shell, args):
    """
    Handle the learning command.
    
    Args:
        shell: The shell instance
        args: Command arguments
    """
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
        success_count = len(history_df[history_df["success"]])
        total_executed = len(history_df[history_df["executed"]])
        if total_executed > 0:
            success_rate = (success_count / total_executed) * 100
            console.print(f"  Success Rate: {success_rate:.1f}% ({success_count}/{total_executed})")

        # Count edited commands
        edited_count = len(history_df[history_df["edited"]])
        console.print(f"  Edited Commands: {edited_count}/{len(history_df)}")

    except Exception as e:
        console.print(f"Error accessing learning store: {e}", style="red")


def handle_export(shell, args):
    """
    Handle the export command.
    
    Args:
        shell: The shell instance
        args: Command arguments
    """
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


def handle_plugins(shell, args):
    """
    Handle the plugins command.
    
    Args:
        shell: The shell instance
        args: Command arguments
    """
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
