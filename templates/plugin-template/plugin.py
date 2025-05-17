"""
Example Plugin Template for PlainSpeak.

This is a template for creating new plugins. Replace this docstring
with a description of your plugin's functionality.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import Plugin, registry, YAMLPlugin
from .platform import platform_manager


class ExamplePlugin(YAMLPlugin):
    """
    Example plugin implementation.

    Features:
    - List your plugin's key features
    - One feature per line
    - Include notable capabilities
    """

    def __init__(self):
        """Initialize the plugin."""
        yaml_path = Path(__file__).parent / "plugin.yaml"
        super().__init__(yaml_path)

        # Add any plugin-specific initialization here
        # Examples:
        # - Load configuration
        # - Initialize resources
        # - Check dependencies

    def _preprocess_args(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess command arguments.

        Args:
            verb: The verb being used.
            args: Original arguments.

        Returns:
            Processed arguments.
        """
        processed = args.copy()

        # Example preprocessing:
        # - Convert paths to platform-specific format
        # - Extract values from natural language
        # - Apply default values
        # - Validate input

        return processed

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a command string.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """
        # Preprocess arguments
        args = self._preprocess_args(verb, args)

        # Add any verb-specific logic here
        if verb == "example-verb":
            # Example: Add default value
            if "option" not in args:
                args["option"] = "default"

        # Generate command using parent's implementation
        return super().generate_command(verb, args)

    def cleanup(self) -> None:
        """Clean up any resources when plugin is unloaded."""
        # Add cleanup code here if needed
        pass


# Create and register the plugin instance
try:
    example_plugin = ExamplePlugin()
    registry.register(example_plugin)
except Exception as e:
    # Log error but don't prevent other plugins from loading
    import logging

    logger = logging.getLogger(__name__)
    logger.warning("Failed to load Example plugin: %s", str(e))
