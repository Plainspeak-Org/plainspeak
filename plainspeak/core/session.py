"""
Session Management for PlainSpeak.

This module handles user sessions, maintaining state and managing
resources across command executions.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from ..context import SessionContext
from ..core.i18n import I18n
from ..core.llm import LLMInterface
from ..core.parser import NaturalLanguageParser

logger = logging.getLogger(__name__)


class Session:
    """
    Manages a user's session with PlainSpeak.

    Handles:
    - Session context and state
    - Resource initialization and cleanup
    - Plugin management
    - Internationalization
    - LLM interface
    """

    def __init__(
        self,
        context: Optional[SessionContext] = None,
        i18n: Optional[I18n] = None,
        llm: Optional[LLMInterface] = None,
        parser: Optional[NaturalLanguageParser] = None,
        plugin_manager=None,
        executor=None,
        working_dir: Optional[str] = None,
    ):
        """
        Initialize a new session.

        Args:
            context: Optional session context instance
            i18n: Optional I18n instance for localization
            llm: Optional LLMInterface instance
            parser: Optional NaturalLanguageParser instance
            plugin_manager: Optional PluginManager instance
            executor: Optional CommandExecutor instance
            working_dir: Optional working directory path
        """
        self.context = context or SessionContext()
        self.i18n = i18n or I18n()
        self.llm_interface = llm or LLMInterface()
        self.parser = parser or NaturalLanguageParser(self.llm_interface)
        self.executor = executor  # May be None

        # Set up working directory if provided
        if working_dir:
            self.context.set_working_dir(working_dir)

        # Set up cross-references
        self.context.i18n = self.i18n
        self.context.llm_interface = self.llm_interface
        self.context.parser = self.parser

        # Initialize plugins
        if plugin_manager:
            self.plugin_manager = plugin_manager
            self.plugins = plugin_manager.get_all_plugins()
        else:
            from ..plugins.manager import PluginManager

            # Create a new plugin manager instance
            self.plugin_manager = PluginManager()
            self.plugins = self.plugin_manager.get_all_plugins()

    def execute_natural_language(self, text: str) -> Tuple[bool, str]:
        """
        Execute a natural language command.

        Args:
            text: Natural language command text

        Returns:
            Tuple of (success, result/error message)
        """
        try:
            command = self.parser.parse_to_command(text)
            if command:
                # Execute the command using appropriate plugin
                result = self.execute_command(command)
                return True, result
            return False, "Failed to parse command"
        except Exception as e:
            logger.error("Error executing natural language command: %s", e)
            return False, str(e)

    def execute_command(self, command: Dict[str, Any]) -> str:
        """
        Execute a parsed command.

        Args:
            command: Parsed command dictionary

        Returns:
            Command execution result
        """
        verb = command.get("verb")
        args = command.get("args", {})

        plugin = self.plugin_manager.find_plugin_for_verb(verb)
        if not plugin:
            if self.i18n:
                error_msg = self.i18n.t("no_plugin_found", {"verb": verb})
            else:
                error_msg = f"No plugin found for verb '{verb}'"
            raise ValueError(error_msg)

        return plugin.generate_command(verb, args)

    def get_context(self) -> SessionContext:
        """Get the current session context."""
        return self.context

    def get_i18n(self) -> I18n:
        """Get the internationalization instance."""
        return self.i18n

    def get_llm(self) -> LLMInterface:
        """Get the LLM interface instance."""
        return self.llm_interface

    def get_parser(self) -> NaturalLanguageParser:
        """Get the parser instance."""
        return self.parser

    def get_plugin(self, name: str):
        """
        Get a plugin by name.

        Args:
            name: Name of the plugin to retrieve

        Returns:
            The plugin instance if found, None otherwise
        """
        return self.plugins.get(name)

    def get_all_plugins(self) -> Dict:
        """Get all available plugins."""
        return self.plugins

    def cleanup(self):
        """Clean up session resources."""
        try:
            # Save context
            self.context.save_context()

            # Clean up plugins
            for plugin in self.plugins.values():
                if hasattr(plugin, "cleanup"):
                    try:
                        plugin.cleanup()
                    except Exception as e:
                        logger.error("Error cleaning up plugin %s: %s", plugin, e)

        except Exception as e:
            logger.error("Error during session cleanup: %s", e)
            raise

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
