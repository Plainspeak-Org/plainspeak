"""Command Line Interface for PlainSpeak.

This module is deprecated. Please use the plainspeak.cli package instead.
It is kept for backward compatibility but will be removed in a future version.
"""

import warnings

from .cli import app, main
from .cli.parser import CommandParser
from .cli.shell import PlainSpeakShell
from .cli.utils import copy_to_clipboard, download_model, initialize_context

# Show a deprecation warning when this module is imported
warnings.warn(
    "The plainspeak.cli module is deprecated. Please use plainspeak.cli.* modules instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Export public API for backward compatibility
__all__ = [
    "app",
    "main",
    "CommandParser",
    "PlainSpeakShell",
    "copy_to_clipboard",
    "download_model",
    "initialize_context",
]

# Make the CLI callable
if __name__ == "__main__":
    main()
