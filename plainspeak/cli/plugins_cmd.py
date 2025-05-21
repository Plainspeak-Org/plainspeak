"""Plugin commands for PlainSpeak CLI."""

from typing import Any, Dict

from rich.console import Console

try:
    from ..plugins import PluginManager, plugin_manager
except ImportError:
    # Mock plugin manager for tests
    class MockPluginManager:
        def get_all_plugins(self) -> Dict[str, Any]:
            return {}

    plugin_manager: PluginManager = MockPluginManager()  # type: ignore

# Create console for rich output
console = Console()


def plugins_command():
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
