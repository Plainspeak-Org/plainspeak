"""
PlainSpeak Plugins Package.

This package contains the plugin system and built-in plugins for PlainSpeak.
"""

import importlib
import pkgutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Plugin registry to store loaded plugins
plugin_registry: Dict[str, Any] = {}


def discover_plugins() -> List[str]:
    """
    Discover available plugins in the plugins directory.

    Returns:
        List of plugin module names.
    """
    plugins_dir = Path(__file__).parent
    return [name for _, name, is_pkg in pkgutil.iter_modules([str(plugins_dir)]) if not name.startswith("_")]


def load_plugin(plugin_name: str) -> Optional[Any]:
    """
    Load a plugin by name.

    Args:
        plugin_name: Name of the plugin module.

    Returns:
        The loaded plugin module, or None if loading failed.
    """
    if plugin_name in plugin_registry:
        return plugin_registry[plugin_name]

    try:
        module = importlib.import_module(f".{plugin_name}", package=__name__)
        plugin_registry[plugin_name] = module
        return module
    except ImportError as e:
        print(f"Error loading plugin {plugin_name}: {e}", file=sys.stderr)
        return None


def load_all_plugins() -> Dict[str, Any]:
    """
    Load all available plugins.

    Returns:
        Dictionary of plugin names to plugin modules.
    """
    plugin_names = discover_plugins()
    for name in plugin_names:
        load_plugin(name)
    return plugin_registry


# Create plugin manager class to handle plugin operations
class PluginManager:
    """
    Plugin Manager for PlainSpeak.

    Handles plugin discovery, loading, and management.
    """

    def __init__(self):
        self.plugins = plugin_registry

    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def get_all_plugins(self) -> Dict[str, Any]:
        """Get all loaded plugins."""
        return self.plugins

    def is_plugin_loaded(self, name: str) -> bool:
        """Check if a plugin is loaded."""
        return name in self.plugins

    def reload_plugins(self) -> Dict[str, Any]:
        """Reload all plugins."""
        return load_all_plugins()


# Load all plugins when the package is imported
load_all_plugins()

# Create a singleton instance of the plugin manager
plugin_manager = PluginManager()
