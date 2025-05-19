"""
Plugin Manager for PlainSpeak.

This module provides the PluginManager class that is responsible for
loading and managing plugins.
"""

import difflib
import importlib
import logging
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml  # type: ignore[import-untyped]

from .base import Plugin, PluginRegistry
from .schemas import PluginManifest

logger = logging.getLogger(__name__)

# Constants
DEFAULT_PLUGIN_PATHS = ["~/.plainspeak/plugins"]


class PluginManager:
    """
    Manager for PlainSpeak plugins.

    This class is responsible for loading plugins from various sources
    (built-in, entry_points, directories) and managing their lifecycle.
    """

    # Configuration for fuzzy matching
    FUZZY_MATCH_THRESHOLD = 0.75
    MAX_FUZZY_MATCHES = 3  # Maximum number of fuzzy matches to consider

    def __init__(self, config=None):
        """
        Initialize the plugin manager.

        Args:
            config: Optional PlainSpeakConfig instance with plugin settings
        """
        self.registry = PluginRegistry()
        self.config = config

        # Get plugin directories from config if available, otherwise use defaults
        if config and hasattr(config, "plugins_dir"):
            self._plugin_dirs = [Path(config.plugins_dir).expanduser()]
        else:
            self._plugin_dirs = [Path(p).expanduser() for p in DEFAULT_PLUGIN_PATHS]

        # Set fuzzy match threshold from config if available
        if config and hasattr(config, "plugin_verb_match_threshold"):
            self.FUZZY_MATCH_THRESHOLD = config.plugin_verb_match_threshold

        self._load_plugins()

    def _load_plugins(self) -> None:
        """
        Load plugins from various sources.

        This method loads plugins from:
        1. Built-in plugins
        2. Entry points
        3. Plugin directories
        """
        self._load_builtin_plugins()
        self._load_plugins_from_entry_points()
        self._load_plugins_from_directories()

        logger.info(f"Loaded {len(self.registry.plugins)} plugins")
        for plugin in self.registry.plugins.values():
            logger.debug(f"Loaded plugin '{plugin.name}' with {len(plugin.get_verbs())} verbs")

    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        try:
            # Import built-in plugins
            from .calendar import CalendarPlugin
            from .email import EmailPlugin
            from .file import FilePlugin
            from .git import GitPlugin
            from .network import NetworkPlugin
            from .system import SystemPlugin
            from .text import TextPlugin

            # Register built-in plugins
            self.registry.register(FilePlugin())
            self.registry.register(SystemPlugin())
            self.registry.register(NetworkPlugin())
            self.registry.register(TextPlugin())
            self.registry.register(GitPlugin())
            self.registry.register(EmailPlugin())
            self.registry.register(CalendarPlugin())

            logger.debug("Loaded built-in plugins")
        except Exception as e:
            logger.error(f"Error loading built-in plugins: {e}", exc_info=True)

    def _load_plugins_from_entry_points(self) -> None:
        """Load plugins from entry points."""
        try:
            import importlib.metadata as metadata
        except ImportError:
            # Python < 3.8
            import importlib_metadata as metadata  # type: ignore[no-redef]

        try:
            for entry_point in metadata.entry_points(group="plainspeak.plugins"):
                try:
                    plugin_class = entry_point.load()
                    plugin = plugin_class()
                    self.registry.register(plugin)
                    logger.debug(f"Loaded plugin '{plugin.name}' from entry point '{entry_point.name}'")
                except Exception as e:
                    logger.error(
                        f"Error loading plugin from entry point '{entry_point.name}': {e}",
                        exc_info=True,
                    )
        except Exception as e:
            logger.error(f"Error loading plugins from entry points: {e}", exc_info=True)

    def _load_plugins_from_directories(self) -> None:
        """Load plugins from plugin directories."""
        for plugin_dir in self._plugin_dirs:
            if not plugin_dir.exists():
                continue

            for plugin_path in plugin_dir.glob("*"):
                if not plugin_path.is_dir():
                    continue

                manifest_path = plugin_path / "manifest.yaml"
                if not manifest_path.exists():
                    continue

                try:
                    with open(manifest_path, "r") as f:
                        manifest_data = yaml.safe_load(f)

                    manifest = PluginManifest(**manifest_data)

                    # Add plugin directory to path if needed
                    if plugin_path not in sys.path:
                        sys.path.append(str(plugin_path))

                    # Import the plugin module
                    module_path, class_name = manifest.entrypoint.rsplit(".", 1)
                    module = importlib.import_module(module_path)
                    plugin_class = getattr(module, class_name)

                    # Create and register the plugin
                    plugin = plugin_class()
                    self.registry.register(plugin)

                    logger.debug(f"Loaded plugin '{plugin.name}' from directory '{plugin_path}'")
                except Exception as e:
                    logger.error(
                        f"Error loading plugin from '{manifest_path}': {e}",
                        exc_info=True,
                    )

    def get_all_plugins(self) -> Dict[str, Plugin]:
        """
        Get all registered plugins.

        Returns:
            Dictionary mapping plugin names to plugin instances.
        """
        return self.registry.plugins

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """
        Get a plugin by name.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin, or None if not found.
        """
        return self.registry.get_plugin(name)

    @lru_cache(maxsize=256)
    def get_all_verbs(self) -> Dict[str, str]:
        """
        Get all verbs from all plugins.

        Returns:
            Dictionary mapping verb to plugin name.
        """
        return self.registry.get_all_verbs()

    @lru_cache(maxsize=256)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:  # type: ignore[no-any-return]
        """
        Get the plugin that can handle the given verb.

        This method attempts to find a plugin for the given verb using the following steps:
        1. Try exact matching (current implementation)
        2. If no exact match, try fuzzy matching

        Args:
            verb: The verb to handle.

        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        if not verb:
            logger.warning("Empty verb provided to get_plugin_for_verb")
            return None

        logger.debug(f"Searching for plugin to handle verb: {verb}")

        # Step 1: Try exact matching via the registry
        plugin = self.registry.get_plugin_for_verb(verb)
        if plugin:
            logger.debug(f"Found exact match for verb '{verb}' in plugin '{plugin.name}'")
            return plugin

        # Step 2: If no exact match, try fuzzy matching
        return self._find_plugin_with_fuzzy_matching(verb)

    def find_plugin_for_verb(self, verb: str) -> Optional[Plugin]:  # type: ignore[no-any-return]
        """
        Alias for get_plugin_for_verb for backwards compatibility.

        Args:
            verb: The verb to handle.

        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        return self.get_plugin_for_verb(verb)

    def _find_plugin_with_fuzzy_matching(self, verb: str) -> Optional[Plugin]:
        """
        Find a plugin using fuzzy matching.

        Args:
            verb: The verb to handle.

        Returns:
            The best matching plugin, or None if no good match found.
        """
        if not verb:
            logger.warning("Empty verb provided to fuzzy matching")
            return None

        verb_lower = verb.lower()
        all_verbs = self.get_all_verbs()

        # No verbs to match against
        if not all_verbs:
            logger.warning("No verbs available for fuzzy matching")
            return None

        try:
            # Find the closest matching verb
            # Get up to MAX_FUZZY_MATCHES potential matches
            matches = difflib.get_close_matches(
                verb_lower,
                [v.lower() for v in all_verbs.keys()],
                n=self.MAX_FUZZY_MATCHES,
                cutoff=self.FUZZY_MATCH_THRESHOLD,
            )

            if not matches:
                logger.debug(f"No fuzzy matches found for verb '{verb}'")
                return None

            # Try each match in order of similarity
            for match in matches:
                # Find the original case of the verb
                for original_verb in all_verbs.keys():
                    if original_verb.lower() == match:
                        plugin_name = all_verbs[original_verb]
                        plugin = self.registry.get_plugin(plugin_name)
                        if plugin:
                            ratio = difflib.SequenceMatcher(None, verb_lower, match).ratio()
                            logger.info(
                                f"Fuzzy matched verb '{verb}' to '{original_verb}' in plugin "
                                f"'{plugin.name}' (similarity: {ratio:.2f})"
                            )
                            return plugin

            # No matching plugin found for any match
            return None
        except Exception as e:
            logger.error(f"Error in fuzzy matching for verb '{verb}': {e}", exc_info=True)
            return None

    def generate_command(self, verb: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Generate a command for the given verb and arguments.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            Tuple of (success, command or error message).
        """
        if not verb:
            logger.warning("Empty verb provided to generate_command")
            return False, "No verb provided"

        plugin = self.get_plugin_for_verb(verb)
        if not plugin:
            logger.warning(f"No plugin found for verb: {verb}")
            return False, f"No plugin found for verb: {verb}"

        try:
            command = plugin.generate_command(verb, args)
            logger.debug(f"Generated command for verb '{verb}' with plugin '{plugin.name}': {command}")
            return True, command
        except Exception as e:
            logger.error(
                f"Error generating command for verb '{verb}' with plugin '{plugin.name}': {e}",
                exc_info=True,
            )
            return False, f"Error generating command: {e}"

    def extract_verb_and_args(self, natural_text: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract the verb and arguments from natural text.

        This is a simple implementation that looks for known verbs at the beginning
        of the text. A more sophisticated implementation would use NLP techniques.

        Args:
            natural_text: The natural language text.

        Returns:
            Tuple of (verb, arguments dictionary).
        """
        if not natural_text:
            logger.warning("Empty or None text provided to extract_verb_and_args")
            return None, {}

        # Get all verbs
        all_verbs = self.get_all_verbs()
        if not all_verbs:
            logger.warning("No verbs available for extraction")
            return None, {}

        # Convert to lowercase for case-insensitive matching
        text_lower = natural_text.lower()

        # Try to find a verb at the beginning of the text
        matched_verb = None
        matched_verb_length = 0

        for verb in all_verbs.keys():
            verb_lower = verb.lower()

            # Check if the text starts with the verb followed by a space or end of text
            if text_lower.startswith(verb_lower) and (
                len(text_lower) == len(verb_lower) or text_lower[len(verb_lower)].isspace()
            ):
                # Use the longest matching verb
                if len(verb) > matched_verb_length:
                    matched_verb = verb
                    matched_verb_length = len(verb)

        if matched_verb:
            # Extract the rest of the text as arguments
            args_text = natural_text[matched_verb_length:].strip()

            # Parse arguments
            args = self._parse_args(args_text)

            logger.debug(f"Extracted verb '{matched_verb}' with args {args} from text: '{natural_text}'")
            return matched_verb, args

        # If no verb found at beginning, try fuzzy matching or more advanced NLP
        logger.debug(f"No verb found at beginning of text: '{natural_text}'")
        return None, {}

    def _parse_args(self, args_text: str) -> Dict[str, Any]:
        """
        Parse arguments from text.

        This is a simple implementation that assumes arguments are in the form:
        - key=value
        - or simply positional parameters

        A more sophisticated implementation would use NLP techniques.

        Args:
            args_text: The arguments text.

        Returns:
            Dictionary of parsed arguments.
        """
        if not args_text:
            return {}

        args = {}
        # Simple named parameter extraction (key=value)
        named_pattern = re.compile(r"(\w+)=([^\s]+)")

        # Extract named parameters
        for match in named_pattern.finditer(args_text):
            key, value = match.groups()
            args[key] = value

        # If no named parameters were found, intelligently assign based on context
        if not args:
            # For file operations (list, find, read, etc.), treat the text as a path
            # This is a very simple heuristic; in practice, we'd use more sophisticated NLP
            if args_text.startswith("/") or "." in args_text or "/" in args_text:
                args["path"] = args_text
            else:
                args["text"] = args_text

        # TODO: Add more sophisticated argument parsing based on context and expected parameters

        return args

    def add_plugin_directory(self, directory: str) -> None:
        """
        Add a directory to search for plugins.

        Args:
            directory: The directory path.
        """
        path = Path(directory).expanduser().resolve()
        if path not in self._plugin_dirs:
            self._plugin_dirs.append(path)
            logger.debug(f"Added plugin directory: {path}")
            # Reload plugins from directories
            self._load_plugins_from_directories()

    def load_plugins(self) -> None:
        """
        Load all plugins.

        This is a public method that delegates to the private _load_plugins method.
        It can be used to explicitly load plugins after initialization.
        """
        logger.info("Loading all plugins")
        self._load_plugins()

    def reload_plugins(self) -> None:
        """
        Reload all plugins.

        This method clears the registry and reloads all plugins.
        Useful when plugin directories or entry points have changed.
        """
        logger.info("Reloading all plugins")
        # Clear the registry
        self.registry = PluginRegistry()
        # Clear caches
        self.get_all_verbs.cache_clear()
        self.get_plugin_for_verb.cache_clear()
        # Reload plugins
        self._load_plugins()


# Global plugin manager
plugin_manager = PluginManager()
