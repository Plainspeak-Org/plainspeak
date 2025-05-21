"""
Argument parsers for PlainSpeak Shell commands.

This module contains the argument parsers used by the PlainSpeak interactive shell.
"""

from cmd2 import Cmd2ArgumentParser


def create_translate_parser():
    """Create and return the argument parser for the translate command."""
    parser = Cmd2ArgumentParser()
    parser.add_argument("text", nargs="+", help="The command description in natural language")
    parser.add_argument("-e", "--execute", action="store_true", help="Execute the translated command")
    return parser


def create_export_parser():
    """Create and return the argument parser for the export command."""
    parser = Cmd2ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: ./plainspeak_training_data.jsonl)",
        default="./plainspeak_training_data.jsonl",
    )
    return parser


def create_exec_parser():
    """Create and return the argument parser for the exec command."""
    parser = Cmd2ArgumentParser()
    parser.add_argument("command", nargs="+", help="The shell command to execute")
    return parser
