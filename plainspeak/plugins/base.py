"""
Base Plugin for PlainSpeak.

This module defines the base plugin class and plugin registry.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, cast
from pathlib import Path
import yaml  # type: ignore[import-untyped]

from .schemas import PluginManifest, CommandConfig, PluginConfig


class Plugin(ABC):
    """
    Base class for PlainSpeak plugins.

    A plugin provides:
    - A name and description
    - A set of verbs it can handle
    - A method to generate commands for those verbs
    """

    def __init__(self, name: str, description: str):
        """
        Initialize the plugin.

        Args:
            name: Plugin name.
            description: Plugin description.
        """
        self.name = name
        self.description = description
        self.verbs: List[str] = []

    @abstractmethod
    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        pass

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
        return verb.lower() in [v.lower() for v in self.get_verbs()]


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

        super().__init__(name=self.manifest.name, description=self.manifest.description)

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
        if verb not in self.manifest.commands:
            raise ValueError(f"Verb '{verb}' not found in plugin '{self.name}'")

        command_config = self.manifest.commands[verb]

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

    def register(self, plugin: Plugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: The plugin to register.
        """
        self.plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin, or None if not found.
        """
        return self.plugins.get(name)

    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        """
        Get the plugin that can handle the given verb.

        Args:
            verb: The verb to handle.

        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        for plugin in self.plugins.values():
            if plugin.can_handle(verb):
                return plugin
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
        return verbs


# Global plugin registry
registry = PluginRegistry()
