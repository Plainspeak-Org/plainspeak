"""
Compatibility module for PlainSpeak CLI.

This module provides backward compatibility for tests and other code that
depends on the old CLI structure.
"""

from ..core.parser import NaturalLanguageParser

# For backward compatibility with tests
CommandParser = NaturalLanguageParser
