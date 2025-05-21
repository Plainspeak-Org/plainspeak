"""
Command handlers for natural language translation.

This module provides the command handler methods for translating natural language to shell commands.
"""

import platform
import re

from rich.console import Console

from ...context import session_context
from ...core.llm import LocalLLMInterface
from ...learning import learning_store
from ..shell_utils import display_command, display_error
from ..utils import download_model
from .execution_handlers import handle_execute

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

    # Display the OS being targeted for command generation
    os_name = platform.system()
    if os_name == "Darwin":
        os_display = "macOS"
    elif os_name == "Windows":
        os_display = "Windows"
    else:
        os_display = "Linux"

    console.print(f"Translating: '{text}'", style="blue")
    console.print(f"Target OS: {os_display}", style="blue dim")

    # Special case for checking if port is open
    if "port" in text.lower() and "open" in text.lower():
        # Attempt to extract port number and host
        port_match = re.search(r"port\s+(\d+)", text.lower())
        host_match = re.search(r"(?:on|at|for)\s+([a-zA-Z0-9.-]+)", text.lower())

        if port_match and host_match:
            port = port_match.group(1)
            host = host_match.group(1)
            result = f"nc -zv {host} {port}"
            display_command(result)

            if args.execute and result.strip():
                handle_execute(shell, result, original_text=text)
            else:
                # Show hints on how to execute the command
                console.print("\nTo execute this command:", style="cyan")
                console.print(f"  Option 1: Type !{result}", style="cyan")
                console.print(f"  Option 2: Type exec {result}", style="cyan")
                console.print(f"  Option 3: Run the same query with -e flag: {text} -e", style="cyan")
            return
        elif port_match:
            port = port_match.group(1)
            # Default to localhost if no host is specified
            result = f"nc -zv localhost {port}"
            display_command(result)

            if args.execute and result.strip():
                handle_execute(shell, result, original_text=text)
            else:
                # Show hints on how to execute the command
                console.print("\nTo execute this command:", style="cyan")
                console.print(f"  Option 1: Type !{result}", style="cyan")
                console.print(f"  Option 2: Type exec {result}", style="cyan")
                console.print(f"  Option 3: Run the same query with -e flag: {text} -e", style="cyan")
            return

    # Special case handling for common queries
    # Memory and process queries
    if "memory" in text.lower() and ("process" in text.lower() or "most" in text.lower()):
        result = "ps aux --sort=-%mem | head -n 10"
        display_command(result)

        if args.execute and result.strip():
            handle_execute(shell, result, original_text=text)
        return

    # File queries - finding large files
    if any(term in text.lower() for term in ["largest file", "biggest file"]):
        if "home" in text.lower():
            result = "find ~ -type f -exec du -sh {} \\; | sort -rh | head -n 10"
        else:
            result = "find . -type f -exec du -sh {} \\; | sort -rh | head -n 10"

        display_command(result)

        if args.execute and result.strip():
            handle_execute(shell, result, original_text=text)
        return

    # System information queries
    if "disk space" in text.lower():
        result = "df -h"
        display_command(result)

        if args.execute and result.strip():
            handle_execute(shell, result, original_text=text)
        return

    # List files queries
    if any(term in text.lower() for term in ["list files", "show files", "display files"]):
        if "by size" in text.lower():
            result = "ls -laSh"
        elif "recent" in text.lower() or "latest" in text.lower():
            result = "ls -lat | head -n 20"
        else:
            result = "ls -la"

        display_command(result)

        if args.execute and result.strip():
            handle_execute(shell, result, original_text=text)
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

            # Handle complex commands where the entire command is already in the verb
            if verb.startswith("for ") or verb.startswith("find "):
                result = verb
                success = True
            else:
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
                from ...config import load_config

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

        # Try to provide fallbacks for common queries
        # Memory queries
        if "memory" in text.lower() and ("process" in text.lower() or "most" in text.lower()):
            console.print("\nFallback suggestion:", style="cyan")
            result = "ps aux --sort=-%mem | head -n 10"
            display_command(result)
            return

        # File operations
        if any(term in text.lower() for term in ["largest file", "biggest file"]):
            console.print("\nFallback suggestion:", style="cyan")
            if "home" in text.lower():
                result = "find ~ -type f -exec du -sh {} \\; | sort -rh | head -n 10"
            else:
                result = "find . -type f -exec du -sh {} \\; | sort -rh | head -n 10"

            display_command(result)
            return
