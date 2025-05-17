"""
PlainSpeak Plugins Package.

This package contains the plugin system and built-in plugins for PlainSpeak.
"""

from pathlib import Path
import importlib
import pkgutil
import sys
from typing import Dict, List, Any, Optional, Type

# Plugin registry to store loaded plugins
plugin_registry: Dict[str, Any] = {}


def discover_plugins() -> List[str]:
    """
    Discover available plugins in the plugins directory.

    Returns:
        List of plugin module names.
    """
    plugins_dir = Path(__file__).parent
    return [
        name
        for _, name, is_pkg in pkgutil.iter_modules([str(plugins_dir)])
        if not name.startswith("_")
    ]


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


# Load all plugins when the package is imported
load_all_plugins()
