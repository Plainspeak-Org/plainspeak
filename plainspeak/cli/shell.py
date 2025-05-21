"""
Interactive shell for PlainSpeak.

This module provides an interactive shell for translating natural language to commands.
"""

from cmd2 import Cmd, with_argparser
from rich.console import Console

from ..context import session_context
from ..core.i18n import I18n
from ..core.llm import LLMInterface
from ..core.parser import NaturalLanguageParser
from .shell_commands import (
    handle_bang,
    handle_context,
    handle_exec,
    handle_execute,
    handle_export,
    handle_history,
    handle_learning,
    handle_plugins,
    handle_translate,
)
from .shell_parsers import create_exec_parser, create_export_parser, create_translate_parser
from .utils import initialize_context

# Create console for rich output
console = Console()


class PlainSpeakShell(Cmd):
    """
    Interactive shell for translating natural language to commands.
    """

    intro = """Welcome to PlainSpeak Shell!
Type your commands in plain English, and they will be translated to shell commands.

Usage:
- Natural language: just type your request (e.g., "find largest files")
- Execute a shell command: start with ! (e.g., "!ls -la")
- Execute a translated command: add -e flag (e.g., "find largest files -e")

Commands are automatically copied to your clipboard for convenience.

Type 'help' for more commands, or 'exit' to quit.\n"""
    prompt = "🗣️ > "

    def __init__(self):
        """Initialize the PlainSpeak shell."""
        super().__init__(allow_cli_args=False)

        # Ensure llm_interface and i18n are initialized before parser
        if (
            not session_context.llm_interface
            or not isinstance(session_context.llm_interface, LLMInterface)
            or not session_context.i18n
            or not isinstance(session_context.i18n, I18n)
        ):
            initialize_context()  # Fallback initialization

        if not session_context.llm_interface or not isinstance(session_context.llm_interface, LLMInterface):
            # If still not initialized, something is critically wrong
            console.print("Critical Error: LLM Interface could not be initialized for PlainSpeakShell.", style="red")
            # Allow to proceed, NaturalLanguageParser might handle None llm if designed for it

        self.parser = NaturalLanguageParser(llm=session_context.llm_interface, i18n=session_context.i18n)

        # Create parsers
        self.translate_parser = create_translate_parser()
        self.export_parser = create_export_parser()
        self.exec_parser = create_exec_parser()

        # Remove some default cmd2 commands we don't need
        self.do_edit = None
        self.do_shortcuts = None
        self.do_shell = None
        self.do_macro = None
        self.do_alias = None
        self.do_run_script = None
        self.do_run_pyscript = None

    @with_argparser(create_translate_parser())
    def do_translate(self, args):
        """Translate natural language to a shell command."""
        handle_translate(self, args, self.translate_parser)

    def do_execute(self, command, original_text=None):
        """Execute a generated command."""
        return handle_execute(self, command, original_text)

    def default(self, statement):
        """Handle unknown commands as natural language input."""
        # Get the original input text from the statement object
        text = getattr(statement, "raw", str(statement)).strip()
        if text:
            # Pass the entire input to translate
            return self.onecmd(f"translate {text}")
        return False

    def do_history(self, args):
        """Show command history."""
        handle_history(self, args)

    def do_context(self, args):
        """Show current session context."""
        handle_context(self, args)

    def do_learning(self, args):
        """Show learning store data."""
        handle_learning(self, args)

    @with_argparser(create_export_parser())
    def do_export(self, args):
        """Export training data from the learning store."""
        handle_export(self, args)

    def do_plugins(self, args):
        """List available plugins and their verbs."""
        handle_plugins(self, args)

    def do_exit(self, _):
        """Exit the shell."""
        # Save context before exiting
        session_context.save_context()
        return True

    @with_argparser(create_exec_parser())
    def do_exec(self, args):
        """Execute a shell command directly without translation."""
        handle_exec(self, args)

    def do_bang(self, args):
        """Shortcut for exec command. Usage: !command args"""
        handle_bang(self, args)

    # Alias ! to the do_bang method
    do_shell = do_bang
