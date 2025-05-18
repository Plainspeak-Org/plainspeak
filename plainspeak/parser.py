"""
Command Parser for PlainSpeak.

This module handles the parsing of natural language into shell commands
using the LLM interface and prompt templates.
"""

from typing import Union

from .ast import Command, Pipeline
from .core.parser import NaturalLanguageParser

# For backward compatibility with tests
CommandParser = NaturalLanguageParser


def parse_command_output(self, command_obj: Union[Command, Pipeline], output: str) -> str:
    """
    Parse command output into natural language.

    Args:
        command_obj: The command that generated the output.
        output: The output to parse.

    Returns:
        Natural language description of the output.
    """
    # For simplicity, we'll just return the output for now
    # TODO: Implement natural language parsing of command output
    return output
