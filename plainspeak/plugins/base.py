"""
Base Plugin for PlainSpeak.

This module defines the base plugin class and plugin registry.
"""

import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml  # type: ignore[import-untyped]

from .schemas import PluginManifest

logger = logging.getLogger(__name__)


class PluginLoadError(Exception):
    """Raised when a plugin fails to load."""


class BasePlugin(ABC):
    """
    Base class for PlainSpeak plugins.

    A plugin provides:
    - A name and description
    - A set of verbs it can handle
    - Methods to check if a verb is supported
    - Support for verb aliases
    - Priority information for conflict resolution
    """

    def __init__(self, name: str, description: str, priority: int = 0):
        """
        Initialize the plugin.

        Args:
            name: Plugin name.
            description: Plugin description.
            priority: Plugin priority (higher values indicate higher priority).
        """
        self.name = name
        self.description = description
        self.verbs: List[str] = []
        self.priority = priority
        # Dictionary mapping aliases to their canonical verb
        self.verb_aliases: Dict[str, str] = {}

        # Cache for verb handling
        self._verb_cache: Dict[str, bool] = {}
        self._canonical_verb_cache: Dict[str, str] = {}

    @abstractmethod
    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """

    def get_aliases(self) -> Dict[str, str]:
        """
        Get all verb aliases mapped to their canonical verbs.

        Returns:
            Dictionary mapping alias to canonical verb.
        """
        return self.verb_aliases

    def get_all_verbs_and_aliases(self) -> List[str]:
        """
        Get all verbs and aliases this plugin can handle.

        Returns:
            List of verbs and aliases.
        """
        return self.get_verbs() + list(self.verb_aliases.keys())

    @abstractmethod
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a command for the given verb and arguments.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """

    def can_handle(self, verb: str) -> bool:
        """
        Check if this plugin can handle the given verb.

        Args:
            verb: The verb to check.

        Returns:
            True if the plugin can handle the verb, False otherwise.
        """
        if not verb:
            return False

        # Check cache first
        verb_lower = verb.lower()
        if verb_lower in self._verb_cache:
            return self._verb_cache[verb_lower]

        result = False

        # Check if it's a canonical verb
        if verb_lower in [v.lower() for v in self.get_verbs()]:
            result = True

        # Check if it's an alias
        elif verb_lower in [a.lower() for a in self.verb_aliases.keys()]:
            result = True

        # Update cache
        self._verb_cache[verb_lower] = result
        return result

    def get_canonical_verb(self, verb: str) -> str:
        """
        Get the canonical verb for the given verb or alias.

        Args:
            verb: The verb or alias to get the canonical verb for.

        Returns:
            The canonical verb.

        Raises:
            ValueError: If the verb is not recognized by this plugin.
        """
        if not verb:
            raise ValueError(f"Empty verb provided to get_canonical_verb")

        # Check cache first
        verb_lower = verb.lower()
        if verb_lower in self._canonical_verb_cache:
            return self._canonical_verb_cache[verb_lower]

        # Check if it's a canonical verb
        for canonical in self.get_verbs():
            if canonical.lower() == verb_lower:
                self._canonical_verb_cache[verb_lower] = canonical
                return canonical

        # Check if it's an alias
        for alias, canonical in self.verb_aliases.items():
            if alias.lower() == verb_lower:
                self._canonical_verb_cache[verb_lower] = canonical
                return canonical

        raise ValueError(f"Verb '{verb}' is not recognized by plugin '{self.name}'")

    def clear_caches(self) -> None:
        """Clear the internal caches for verb handling."""
        self._verb_cache.clear()
        self._canonical_verb_cache.clear()


class YAMLPlugin(BasePlugin):
    """
    Plugin implementation that loads configuration from a YAML manifest.

    The manifest should follow the PluginManifest schema.
    """

    def __init__(self, manifest_path: Path):
        """
        Initialize a plugin from a YAML manifest file.

        Args:
            manifest_path: Path to the manifest YAML file.
        """
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

        # Initialize with data from manifest
        super().__init__(
            name=self.manifest.name,
            description=self.manifest.description,
            priority=self.manifest.priority,
        )

        # Load verb aliases from manifest
        for verb, aliases in self.manifest.verb_aliases.items():
            for alias in aliases:
                self.verb_aliases[alias] = verb

    def _load_manifest(self) -> PluginManifest:
        """
        Load and validate the YAML manifest.

        Returns:
            Validated PluginManifest.

        Raises:
            PluginLoadError: If the manifest is invalid or cannot be loaded.
        """
        try:
            with open(self.manifest_path, "r") as f:
                manifest_data = yaml.safe_load(f)

            # Validate using Pydantic
            return PluginManifest(**manifest_data)
        except Exception as e:
            error_msg = f"Failed to load manifest from {self.manifest_path}: {e}"
            logger.error(error_msg)
            raise PluginLoadError(error_msg) from e

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verbs from the manifest.
        """
        return self.manifest.verbs

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a command using the template from the manifest.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.

        Raises:
            ValueError: If the verb is not supported or the template is missing.
        """
        # Check if the verb is valid
        if not self.can_handle(verb):
            raise ValueError(f"Plugin '{self.name}' cannot handle verb '{verb}'")

        # Get the canonical verb if it's an alias
        canonical_verb = self.get_canonical_verb(verb)

        # Check if the command exists in the manifest
        if canonical_verb not in self.manifest.commands:
            raise ValueError(f"No command template found for verb '{canonical_verb}' in plugin '{self.name}'")

        # Get the command template
        command_config = self.manifest.commands[canonical_verb]

        # Apply the template (basic implementation, should use Jinja2 in practice)
        command = command_config.template

        # Replace placeholders with argument values
        for key, value in args.items():
            placeholder = f"{{{{ {key} }}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(value))

        return command


class PluginRegistry:
    """
    Registry for PlainSpeak plugins.

    This class manages the loading and lookup of plugins.
    It provides:
    - Methods to register plugins
    - Methods to look up plugins by name or verb
    - LRU caching for verb lookups
    - Priority-based conflict resolution
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, BasePlugin] = {}
        self.verb_to_plugin_cache: Dict[str, str] = {}

    def register(self, plugin: BasePlugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: The plugin to register.
        """
        if plugin.name in self.plugins:
            logger.warning(f"Replacing existing plugin '{plugin.name}'")

        self.plugins[plugin.name] = plugin

        # Clear the cache when registering a new plugin
        self.verb_to_plugin_cache.clear()

        # Log plugin registration
        logger.debug(
            f"Registered plugin '{plugin.name}' with {len(plugin.get_verbs())} verbs "
            f"and {len(plugin.get_aliases())} aliases"
        )

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a plugin by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin, or None if not found.
        """
        return self.plugins.get(name)

    @lru_cache(maxsize=256)
    def get_plugin_for_verb(self, verb: str) -> Optional[BasePlugin]:
        """
        Get the plugin that can handle the given verb.

        This method finds the plugin for a verb while respecting plugin priorities.
        Plugins with higher priority values are preferred when multiple plugins
        can handle the same verb.

        Args:
            verb: The verb to handle.

        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        if not verb:
            logger.debug("Empty verb provided to get_plugin_for_verb")
            return None

        verb_lower = verb.lower()

        # First, try to find an exact match
        matching_plugins: List[Tuple[int, BasePlugin]] = []

        for plugin in self.plugins.values():
            if plugin.can_handle(verb_lower):
                matching_plugins.append((plugin.priority, plugin))

        # Sort by priority (highest first)
        if matching_plugins:
            matching_plugins.sort(reverse=True)
            selected_plugin = matching_plugins[0][1]

            logger.debug(
                f"Found plugin '{selected_plugin.name}' for verb '{verb}' " f"(priority: {selected_plugin.priority})"
            )

            if len(matching_plugins) > 1:
                # Log when multiple plugins can handle the same verb
                logger.debug(
                    f"Multiple plugins can handle verb '{verb}': "
                    + ", ".join([f"'{p[1].name}' (priority: {p[0]})" for p in matching_plugins])
                )

            return selected_plugin

        # No match found
        return None

    def get_all_verbs(self) -> Dict[str, str]:
        """
        Get all verbs from all plugins.

        Returns:
            Dictionary mapping verb to plugin name.
        """
        verbs = {}
        for plugin in self.plugins.values():
            for verb in plugin.get_verbs():
                verbs[verb] = plugin.name
            # Include aliases
            for alias, canonical in plugin.get_aliases().items():
                verbs[alias] = plugin.name
        return verbs

    def clear_caches(self) -> None:
        """
        Clear all caches in the registry and plugins.

        Call this method when plugins are added or removed, or when
        plugin configurations change.
        """
        # Clear the registry's LRU cache
        self.get_plugin_for_verb.cache_clear()

        # Clear verb_to_plugin_cache
        self.verb_to_plugin_cache.clear()

        # Clear caches in all plugins
        for plugin in self.plugins.values():
            if hasattr(plugin, "clear_caches"):
                plugin.clear_caches()

    def get_plugins_sorted_by_priority(self) -> List[BasePlugin]:
        """
        Get all plugins sorted by priority (highest first).

        Returns:
            List of plugins sorted by priority.
        """
        plugins = list(self.plugins.values())
        plugins.sort(key=lambda p: p.priority, reverse=True)
        return plugins


# Global plugin registry instance
registry = PluginRegistry()

# Backwards compatibility
Plugin = BasePlugin  # For backwards compatibility with existing code
