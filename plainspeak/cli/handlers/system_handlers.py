"""
Command handlers for system information and utility commands.

This module provides the command handlers for interacting with system context, history,
learning store, and plugins.
"""

from pathlib import Path

from rich.console import Console

from ...context import session_context
from ...learning import learning_store
from ...plugins import plugin_manager

# Create console for rich output
console = Console()


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
