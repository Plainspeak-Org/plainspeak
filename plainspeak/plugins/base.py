"""
Base Plugin for PlainSpeak.

This module defines the base plugin class and plugin registry.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, cast, Set, Tuple
from pathlib import Path
import yaml  # type: ignore[import-untyped]
import logging
from functools import lru_cache

from .schemas import PluginManifest, CommandConfig, PluginConfig

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """
    Base class for PlainSpeak plugins.

    A plugin provides:
    - A name and description
    - A set of verbs it can handle
    - A method to generate commands for those verbs
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

    @abstractmethod
    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        pass

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
        pass

    def can_handle(self, verb: str) -> bool:
        """
        Check if this plugin can handle the given verb.

        Args:
            verb: The verb to check.

        Returns:
            True if the plugin can handle the verb, False otherwise.
        """
        verb_lower = verb.lower()
        
        # Check if it's a canonical verb
        if verb_lower in [v.lower() for v in self.get_verbs()]:
            return True
            
        # Check if it's an alias
        if verb_lower in [a.lower() for a in self.verb_aliases.keys()]:
            return True
            
        return False

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
        verb_lower = verb.lower()
        
        # Check if it's a canonical verb
        for canonical in self.get_verbs():
            if canonical.lower() == verb_lower:
                return canonical
                
        # Check if it's an alias
        for alias, canonical in self.verb_aliases.items():
            if alias.lower() == verb_lower:
                return canonical
                
        raise ValueError(f"Verb '{verb}' is not recognized by plugin '{self.name}'")


class YAMLPlugin(Plugin):
    """
    A plugin that loads its configuration from a YAML file.

    The YAML file should have the following structure:
    ```yaml
    name: Plugin Name
    description: Plugin description
    verbs:
      - verb1
      - verb2
    commands:
      verb1:
        template: "command {{ arg1 }} {{ arg2 }}"
        description: Description of verb1
        examples:
          - "Example usage of verb1"
      verb2:
        template: "another-command {{ arg1 }}"
        description: Description of verb2
        examples:
          - "Example usage of verb2"
    ```
    """

    def __init__(self, yaml_path: Path):
        """
        Initialize the plugin from a YAML file.

        Args:
            yaml_path: Path to the YAML configuration file.

        Raises:
            ValueError: If the YAML configuration is invalid.
        """
        self.yaml_path = yaml_path
        yaml_data = self._load_yaml()

        # Validate against schema
        try:
            self.manifest = PluginManifest.parse_obj(yaml_data)
            self.config = PluginConfig(
                manifest=self.manifest, instance=self, enabled=True, load_error=None
            )
        except Exception as e:
            raise ValueError(f"Invalid plugin manifest: {e}")

        super().__init__(
            name=self.manifest.name, 
            description=self.manifest.description,
            priority=self.manifest.priority
        )
        
        # Process verb aliases
        self.verb_aliases = {}
        for canonical, aliases in self.manifest.verb_aliases.items():
            for alias in aliases:
                self.verb_aliases[alias] = canonical
                
        # Process command aliases
        for verb, command_config in self.manifest.commands.items():
            for alias in command_config.aliases:
                self.verb_aliases[alias] = verb

    def _load_yaml(self) -> Dict[str, Any]:  # type: ignore[no-any-return]
        """
        Load the YAML configuration file.

        Returns:
            The parsed YAML data.
        """
        with open(self.yaml_path, "r") as f:
            return yaml.safe_load(f)

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs from the manifest.

        Returns:
            List of verb strings.
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
            ValueError: If the verb is not found or required arguments are missing.
        """
        # Convert alias to canonical verb if needed
        canonical_verb = verb
        try:
            canonical_verb = self.get_canonical_verb(verb)
        except ValueError:
            pass
            
        if canonical_verb not in self.manifest.commands:
            raise ValueError(f"Verb '{verb}' not found in plugin '{self.name}'")

        command_config = self.manifest.commands[canonical_verb]

        # Validate required arguments
        missing_args = [arg for arg in command_config.required_args if arg not in args]
        if missing_args:
            raise ValueError(
                f"Missing required arguments for verb '{verb}': {', '.join(missing_args)}"
            )

        # Add default values for missing optional arguments
        for arg, default in command_config.optional_args.items():
            if arg not in args:
                args[arg] = default

        # Render template with arguments
        template = command_config.template
        try:
            for key, value in args.items():
                placeholder = f"{{ {key} }}"
                template = template.replace(placeholder, str(value))
            return template
        except Exception as e:
            raise ValueError(f"Error rendering command template: {e}")


class PluginRegistry:
    """
    Registry for PlainSpeak plugins.

    This class manages the loading and lookup of plugins.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self.plugins: Dict[str, Plugin] = {}
        self.verb_to_plugin_cache: Dict[str, str] = {}

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: The plugin to register.
        """
        self.plugins[plugin.name] = plugin
        # Clear the cache when registering a new plugin
        self.verb_to_plugin_cache.clear()

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin, or None if not found.
        """
        return self.plugins.get(name)

    @lru_cache(maxsize=128)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        """
        Get the plugin that can handle the given verb.

        Args:
            verb: The verb to handle.

        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        verb_lower = verb.lower()
        
        # First, try to find an exact match
        matching_plugins: List[Tuple[int, Plugin]] = []
        
        for plugin in self.plugins.values():
            if plugin.can_handle(verb_lower):
                matching_plugins.append((plugin.priority, plugin))
                
        # Sort by priority (highest first)
        if matching_plugins:
            matching_plugins.sort(reverse=True)
            return matching_plugins[0][1]
            
        # If no exact match, we could implement fuzzy matching here
        
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


# Global plugin registry
registry = PluginRegistry()
