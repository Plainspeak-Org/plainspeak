"""
Abstract Syntax Tree for PlainSpeak.

This module defines the structured representation of commands
and their relationships.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CommandType(Enum):
    """Types of commands that can be represented."""

    SHELL = "shell"  # Basic shell commands
    PLUGIN = "plugin"  # Plugin-specific commands
    COMPOUND = "compound"  # Multiple commands (e.g., pipeline)
    CONTROL = "control"  # Control flow (if, for, etc.)


class ArgumentType(Enum):
    """Types of arguments that can be passed to commands."""

    FLAG = "flag"  # Boolean flags (e.g., -f, --force)
    OPTION = "option"  # Key-value options (e.g., --name=value)
    POSITIONAL = "pos"  # Positional arguments
    PATH = "path"  # File or directory paths
    PATTERN = "pattern"  # Search patterns or globs
    EXPRESSION = "expr"  # Expressions (e.g., arithmetic)


@dataclass
class Argument:
    """Represents a command argument."""

    type: ArgumentType
    value: Union[str, bool, int, float, Path]
    name: Optional[str] = None  # For named options
    original_text: Optional[str] = None  # Original natural language description


@dataclass
class Plugin:
    """Reference to a plugin that can handle a command."""

    name: str
    verbs: List[str]
    context: Optional[Dict[str, Any]] = None


@dataclass
class Command:
    """
    Represents a single command in the AST.

    Examples:
    - Simple shell: ls -l /path
    - Plugin command: file.copy source dest --recursive
    - Compound: grep pattern file | sort
    """

    type: CommandType
    name: str  # Command name or verb
    args: List[Argument]  # Arguments and options
    plugin: Optional[Plugin] = None  # Associated plugin if any
    input_text: Optional[str] = None  # Original natural language input
    metadata: Optional[Dict[str, Any]] = None  # Additional context/metadata


@dataclass
class Pipeline:
    """
    Represents a pipeline of commands.

    Example: find . -type f | grep pattern | sort
    """

    commands: List[Command]
    original_text: Optional[str] = None


class ASTBuilder:
    """
    Builds an AST from natural language input or command strings.

    Features:
    - Natural language parsing with LLM assistance
    - Command string parsing
    - Plugin integration
    - Pattern matching from learning system
    """

    def __init__(self):
        """Initialize the AST builder."""
        self.command_patterns = {}  # Cache of known patterns

    def _detect_argument_type(self, arg: str) -> ArgumentType:
        """
        Detect the type of an argument.

        Args:
            arg: The argument string.

        Returns:
            ArgumentType enum value.
        """
        if arg.startswith(("-", "--")):
            if "=" in arg:
                return ArgumentType.OPTION
            return ArgumentType.FLAG
        elif "/" in arg or "\\" in arg:
            return ArgumentType.PATH
        elif "*" in arg or "?" in arg:
            return ArgumentType.PATTERN
        return ArgumentType.POSITIONAL

    def _parse_plugin_command(self, plugin: Plugin, verb: str, args_dict: Dict[str, Any]) -> Command:
        """
        Parse a plugin command from verb and arguments.

        Args:
            plugin: The plugin reference.
            verb: The verb to use.
            args_dict: Dictionary of argument name/value pairs.

        Returns:
            Command object for the plugin command.
        """
        args = []
        for name, value in args_dict.items():
            arg_type = self._detect_argument_type(str(value))
            args.append(Argument(type=arg_type, value=value, name=name))

        return Command(type=CommandType.PLUGIN, name=verb, args=args, plugin=plugin)

    def _parse_shell_command(self, command_str: str) -> Command:
        """
        Parse a shell command string.

        Args:
            command_str: The command string to parse.

        Returns:
            Command object for the shell command.
        """
        parts = command_str.split()
        if not parts:
            raise ValueError("Empty command")

        args = []
        name = parts[0]

        for part in parts[1:]:
            arg_type = self._detect_argument_type(part)
            if arg_type == ArgumentType.OPTION:
                opt_name, opt_value = part.split("=", 1)
                args.append(Argument(type=arg_type, value=opt_value, name=opt_name.lstrip("-")))
            else:
                args.append(Argument(type=arg_type, value=part))

        return Command(type=CommandType.SHELL, name=name, args=args)

    def from_natural_language(self, text: str, context: Optional[Dict[str, Any]] = None) -> Union[Command, Pipeline]:
        """
        Build AST from natural language input.

        Args:
            text: Natural language description.
            context: Optional context information.

        Returns:
            Command or Pipeline object.
        """
        # TODO: Use LLM to identify command structure
        # For now, try plugin-based parsing
        from .plugins.manager import PluginManager

        # Get the plugin manager instance
        plugin_manager = PluginManager()

        verb, args = plugin_manager.extract_verb_and_args(text)
        if verb:
            plugin = plugin_manager.get_plugin_for_verb(verb)
            if plugin:
                # Build plugin command
                return self._parse_plugin_command(
                    Plugin(name=plugin.name, verbs=plugin.get_verbs(), context=context),
                    verb,
                    args,
                )

        # Fallback to shell command parsing
        # TODO: Use LLM to generate command first
        return self._parse_shell_command(text)

    def from_command_string(self, command: str, original_text: Optional[str] = None) -> Union[Command, Pipeline]:
        """
        Build AST from a command string.

        Args:
            command: The command string to parse.
            original_text: Optional natural language description.

        Returns:
            Command or Pipeline object.
        """
        if "|" in command:
            # Split pipeline and parse each command
            commands = []
            for cmd in command.split("|"):
                commands.append(self._parse_shell_command(cmd.strip()))
            return Pipeline(commands=commands, original_text=original_text)

        return self._parse_shell_command(command)


# Global AST builder instance
ast_builder = ASTBuilder()
