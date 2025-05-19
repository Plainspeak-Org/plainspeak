"""
Base Plugin for PlainSpeak.

This module defines the base plugin class and plugin registry.
"""

import logging
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml  # type: ignore[import-untyped]

from .schemas import PluginManifest

logger = logging.getLogger(__name__)


class PluginLoadError(Exception):
    """Raised when a plugin fails to load."""


class BasePlugin(ABC):
    """Base class for PlainSpeak plugins."""

    def __init__(self, name: str, description: str, priority: int = 0):
        """Initialize plugin."""
        self.name = name
        self.description = description
        self.verbs: List[str] = []
        self.priority = priority
        self.verb_aliases: Dict[str, str] = {}  # alias -> canonical verb
        self._verb_cache: Dict[str, bool] = {}
        self._canonical_verb_cache: Dict[str, str] = {}

    @abstractmethod
    def get_verbs(self) -> List[str]:
        """Get supported verbs."""

    def get_aliases(self) -> Dict[str, str]:
        """Get verb aliases."""
        return self.verb_aliases

    def get_all_verbs_and_aliases(self) -> List[str]:
        """Get all verbs and aliases."""
        return self.get_verbs() + list(self.verb_aliases.keys())

    @abstractmethod
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """Generate command for verb."""

    def can_handle(self, verb: str) -> bool:
        """Check if plugin can handle verb."""
        if not verb:
            return False

        verb_lower = verb.lower()
        if verb_lower in self._verb_cache:
            return self._verb_cache[verb_lower]

        can_handle = verb_lower in [v.lower() for v in self.get_verbs()] or verb_lower in [
            a.lower() for a in self.verb_aliases
        ]
        self._verb_cache[verb_lower] = can_handle
        return can_handle

    def get_canonical_verb(self, verb: str) -> str:
        """Get canonical form of verb."""
        if not verb:
            raise ValueError("Empty verb provided")

        verb_lower = verb.lower()
        if verb_lower in self._canonical_verb_cache:
            return self._canonical_verb_cache[verb_lower]

        # Check canonical verbs
        for canonical in self.get_verbs():
            if canonical.lower() == verb_lower:
                self._canonical_verb_cache[verb_lower] = canonical
                return canonical

        # Check aliases
        for alias, canonical in self.verb_aliases.items():
            if alias.lower() == verb_lower:
                self._canonical_verb_cache[verb_lower] = canonical
                return canonical

        raise ValueError(f"Verb '{verb}' not recognized by plugin '{self.name}'")

    def clear_caches(self) -> None:
        """Clear verb caches."""
        self._verb_cache.clear()
        self._canonical_verb_cache.clear()

    def get_verb_details(self, verb: str) -> Dict[str, Any]:
        """
        Get details about a verb.

        Args:
            verb: The verb to get details for.

        Returns:
            Dictionary with verb details.
        """
        if not self.can_handle(verb):
            return {}

        canonical = self.get_canonical_verb(verb)

        # Basic details that all plugins should provide
        details = {
            "verb": canonical,
            "plugin": self.name,
            "description": f"{canonical} command from {self.name} plugin",
            "args": {},
            "template": f"{canonical} {{args}}",  # Default template
            "action_type": "execute_command",  # Default action type
        }

        # Add any additional details specific to the plugin implementation
        return details

    def __lt__(self, other):
        """Compare by priority."""
        if isinstance(other, BasePlugin):
            return self.priority < other.priority
        return NotImplemented


class YAMLPlugin(BasePlugin):
    """Plugin loaded from YAML manifest."""

    def __init__(self, manifest_path: str):
        """Initialize from manifest."""
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()

        super().__init__(
            name=self.manifest.name,
            description=self.manifest.description,
            priority=self.manifest.priority,
        )

        # Load aliases
        for verb, aliases in self.manifest.verb_aliases.items():
            for alias in aliases:
                self.verb_aliases[alias] = verb

    def _load_manifest(self) -> PluginManifest:
        """Load and validate manifest."""
        try:
            with open(self.manifest_path, "r") as f:
                manifest_data = yaml.safe_load(f)
            return PluginManifest(**manifest_data)
        except Exception as e:
            error_msg = f"Failed to load manifest from {self.manifest_path}: {e}"
            logger.error(error_msg)
            raise PluginLoadError(error_msg) from e

    def get_verbs(self) -> List[str]:
        """Get supported verbs."""
        return self.manifest.verbs

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """Generate command from template."""
        if not self.can_handle(verb):
            raise ValueError(f"Plugin '{self.name}' cannot handle verb '{verb}'")

        canonical = self.get_canonical_verb(verb)
        if canonical not in self.manifest.commands:
            raise ValueError(f"No command template for verb '{canonical}'")

        command = self.manifest.commands[canonical].template
        for key, value in args.items():
            placeholder = f"{{{{ {key} }}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(value))
        return command


class PluginRegistry:
    """Registry managing plugins."""

    def __init__(self):
        """Initialize registry."""
        self.plugins: Dict[str, BasePlugin] = {}
        self.verb_to_plugin_map: Dict[str, str] = {}
        self.verb_to_plugin_cache: Dict[str, str] = {}

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin."""
        if plugin.name in self.plugins:
            logger.warning(f"Replacing plugin '{plugin.name}'")
        self.plugins[plugin.name] = plugin
        self._rebuild_verb_maps()
        logger.debug(
            f"Registered plugin '{plugin.name}' with {len(plugin.get_verbs())} verbs "
            f"and {len(plugin.get_aliases())} aliases"
        )

    def _rebuild_verb_maps(self) -> None:
        """Rebuild verb mappings."""
        self.verb_to_plugin_map.clear()
        self.verb_to_plugin_cache.clear()
        self.get_plugin_for_verb.cache_clear()

        # Process plugins in priority order
        plugins = self.get_plugins_sorted_by_priority()
        for plugin in plugins:
            for verb in plugin.get_verbs():
                if verb.lower() not in self.verb_to_plugin_map:
                    self.verb_to_plugin_map[verb.lower()] = plugin.name
            for alias in plugin.get_aliases():
                if alias.lower() not in self.verb_to_plugin_map:
                    self.verb_to_plugin_map[alias.lower()] = plugin.name

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)

    @lru_cache(maxsize=256)
    def get_plugin_for_verb(self, verb: str) -> Optional[BasePlugin]:
        """Get plugin for verb."""
        if not verb:
            logger.debug("Empty verb provided")
            return None

        verb_lower = verb.lower()
        plugin_name = self.verb_to_plugin_map.get(verb_lower)
        if plugin_name:
            # Handle case where plugin was removed but still in verb map
            if plugin_name in self.plugins:
                return self.plugins[plugin_name]
            else:
                logger.warning(f"Plugin '{plugin_name}' for verb '{verb}' not found in registry")
                # Clear caches to rebuild verb maps
                self.clear_caches()
                return None

        return None

    def get_all_verbs(self) -> Dict[str, str]:
        """Get all verb mappings."""
        return self.verb_to_plugin_map.copy()

    def get_plugins_sorted_by_priority(self) -> List[BasePlugin]:
        """Get plugins sorted by priority."""
        plugins = list(self.plugins.values())
        plugins.sort(key=lambda p: p.priority, reverse=True)
        return plugins

    def clear(self) -> None:
        """Clear registry."""
        self.plugins.clear()
        self.verb_to_plugin_map.clear()
        self.verb_to_plugin_cache.clear()
        self.get_plugin_for_verb.cache_clear()

    def clear_caches(self) -> None:
        """Clear caches but keep plugins."""
        self.verb_to_plugin_map.clear()
        self.verb_to_plugin_cache.clear()
        self.get_plugin_for_verb.cache_clear()

        # Also clear caches in plugins
        for plugin in self.plugins.values():
            if hasattr(plugin, "clear_caches"):
                plugin.clear_caches()


# Global registry
registry = PluginRegistry()

# Backwards compatibility
Plugin = BasePlugin
