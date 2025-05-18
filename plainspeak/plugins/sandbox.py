"""
Safety Sandbox Plugin for PlainSpeak.

This module extends the core sandbox functionality with plugin-specific features.
"""

import logging
from typing import Optional, Tuple

from ..core.sandbox import Sandbox

logger = logging.getLogger(__name__)


class SafetySandbox(Sandbox):
    """
    Enhanced safety sandbox plugin that extends core sandbox functionality.

    Features:
    - Inherits all core sandbox safety features
    - Can be extended with plugin-specific validation rules
    - Plugin-specific command execution customization
    """

    def __init__(self):
        """Initialize the sandbox plugin."""
        super().__init__()

    def validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Extends core validation with plugin-specific rules.

        Args:
            command: The command to validate.

        Returns:
            Tuple of (is_safe, error_message).
        """
        # First run core validation
        is_safe, error = super().validate_command(command)
        if not is_safe:
            return False, error

        # Add any plugin-specific validation here
        return True, None


# Global sandbox instance
sandbox = SafetySandbox()
