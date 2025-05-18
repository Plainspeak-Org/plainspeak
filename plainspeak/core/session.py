"""
Session Management for PlainSpeak.

This module handles user sessions, maintaining state and managing
resources across command executions.
"""

import logging
from typing import Dict, Optional

from ..context import SessionContext
from ..core.i18n import I18n
from ..core.llm import LLMInterface
from ..plugins.manager import plugin_manager

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
        self, context: Optional[SessionContext] = None, i18n: Optional[I18n] = None, llm: Optional[LLMInterface] = None
    ):
        """
        Initialize a new session.

        Args:
            context: Optional session context instance
            i18n: Optional I18n instance for localization
            llm: Optional LLMInterface instance
        """
        self.context = context or SessionContext()
        self.i18n = i18n or I18n()
        self.llm_interface = llm or LLMInterface()

        # Set up cross-references
        self.context.i18n = self.i18n
        self.context.llm_interface = self.llm_interface

        # Initialize plugins
        self.plugins = plugin_manager.get_all_plugins()

    def get_context(self) -> SessionContext:
        """Get the current session context."""
        return self.context

    def get_i18n(self) -> I18n:
        """Get the internationalization instance."""
        return self.i18n

    def get_llm(self) -> LLMInterface:
        """Get the LLM interface instance."""
        return self.llm_interface

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
