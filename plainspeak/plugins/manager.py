"""Plugin manager for PlainSpeak."""

import importlib
import logging
from typing import Any, Dict, Optional

import yaml

from plainspeak.plugins.base import BasePlugin, PluginRegistry
from plainspeak.plugins.schemas import PluginManifest
from plainspeak.utils import paths

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages plugins for PlainSpeak."""

    def __init__(self, config=None):
        """Initialize plugin manager."""
        self.config = config
        self.registry = PluginRegistry()
        self._load_plugins()

    def _load_plugins(self) -> None:
        """Load all plugins."""
        # First load builtin plugins
        self._load_builtin_plugins()

        # Then load any additional plugins from entry points
        self._load_plugins_from_entry_points()

        # Finally load plugins from configured directories
        self._load_plugins_from_directories()

        if not self.registry.plugins:
            logger.warning("No plugins were loaded!")

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        try:
            from plainspeak.plugins import file, network, system, text

            self.registry.register(file.FilePlugin())
            self.registry.register(text.TextPlugin())
            self.registry.register(system.SystemPlugin())
            self.registry.register(network.NetworkPlugin())
        except Exception as e:
            logger.error(f"Error loading builtin plugins: {e}")

    def _load_plugins_from_entry_points(self) -> None:
        """Load plugins from setuptools entry points."""
        try:
            import importlib.metadata as metadata

            for entry_point in metadata.entry_points(group="plainspeak.plugins"):
                try:
                    if (
                        self.config
                        and hasattr(self.config, "plugins_enabled")
                        and self.config.plugins_enabled
                        and entry_point.name not in self.config.plugins_enabled
                    ):
                        logger.debug(f"Skipping disabled plugin: {entry_point.name}")
                        continue

                    plugin_class = entry_point.load()
                    plugin = plugin_class()

                    if self.config and hasattr(self.config, "plugins_disabled"):
                        if plugin.name in self.config.plugins_disabled:
                            logger.info(f"Plugin '{plugin.name}' is disabled in configuration")
                            continue

                    self.registry.register(plugin)
                    logger.debug(f"Loaded plugin '{plugin.name}' from entry point")

                except Exception as e:
                    logger.error(f"Error loading plugin from entry point '{entry_point.name}': {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error loading plugins from entry points: {e}", exc_info=True)

    def _load_plugins_from_directories(self) -> None:
        """Load plugins from directories."""
        if not self.config or not hasattr(self.config, "plugins_dir"):
            return

        plugins_dir = self.config.plugins_dir
        if not paths.exists(plugins_dir):
            logger.warning(f"Plugins directory does not exist: {plugins_dir}")
            return

        # List plugin directories
        try:
            entries = paths.list_directory(plugins_dir)
            plugin_dirs = []

            # First collect all plugin directories
            for entry in entries:
                if paths.is_directory(entry):
                    manifest_path = paths.join_paths(entry, "manifest.yaml")
                    if paths.exists(manifest_path):
                        plugin_dirs.append(entry)

            # Load plugins from each directory
            for plugin_dir in plugin_dirs:
                try:
                    manifest_path = paths.join_paths(plugin_dir, "manifest.yaml")
                    with open(manifest_path) as f:
                        manifest_data = yaml.safe_load(f)

                    # Validate manifest data
                    manifest = PluginManifest(**manifest_data)

                    # Import the plugin module and class
                    module_name, class_name = manifest.entrypoint.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    plugin_class = getattr(module, class_name)

                    # Instantiate and register plugin
                    plugin = plugin_class()
                    self.registry.register(plugin)
                    logger.debug(f"Loaded plugin '{plugin.name}' from {manifest_path}")

                except Exception as e:
                    logger.error(f"Error loading plugin from {manifest_path}: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Error scanning plugins directory: {e}", exc_info=True)

    def get_plugin_for_verb(self, verb: str) -> Optional[BasePlugin]:
        """
        Get the plugin that can handle the given verb.

        Args:
            verb: The verb to handle.

        Returns:
            Plugin instance or None if no plugin found.
        """
        return self.registry.get_plugin_for_verb(verb)

    def find_plugin_for_verb(self, verb: str) -> Optional[BasePlugin]:
        """
        Find the plugin that can handle the given verb.

        This is an alias for get_plugin_for_verb for backward compatibility.

        Args:
            verb: The verb to handle.

        Returns:
            Plugin instance or None if no plugin found.
        """
        return self.get_plugin_for_verb(verb)

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.

        Args:
            name: Name of the plugin.

        Returns:
            Plugin instance or None if not found.
        """
        return self.registry.plugins.get(name)

    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """
        Get all registered plugins.

        Returns:
            Dictionary of plugin name to plugin instance.
        """
        return self.registry.plugins

    def get_all_verbs(self) -> Dict[str, str]:
        """
        Get all available verbs.

        Returns:
            Dictionary of verb to plugin name.
        """
        return self.registry.get_all_verbs()

    def get_verb_details(self, verb: str) -> Dict[str, Any]:
        """
        Get details about a verb's parameters and usage.

        Args:
            verb: The verb to get details for.

        Returns:
            Dictionary with verb details.
        """
        plugin = self.get_plugin_for_verb(verb)
        if not plugin:
            return {}
        return plugin.get_verb_details(verb)

    def reload_plugins(self) -> None:
        """Reload all plugins."""
        self.registry.clear()
        self._load_plugins()
