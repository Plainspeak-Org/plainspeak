"""
REPL Interface for PlainSpeak.

This module provides a Read-Eval-Print Loop (REPL) interface for PlainSpeak.
"""

from typing import Optional, Tuple

from .core.session import Session


class REPLInterface:
    """
    Read-Eval-Print Loop (REPL) interface for PlainSpeak.

    This class provides a simple REPL interface for PlainSpeak, allowing users
    to enter natural language commands and see the results.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize the REPL interface.

        Args:
            session: The PlainSpeak session to use. If None, a new session will be created.
        """
        self.session = session or Session()
        self.running = False

    def run(self):
        """Run the REPL loop."""
        self.running = True
        self.print_welcome()
        self.cmdloop()

    def cmdloop(self):
        """Run the command loop."""
        while self.running:
            try:
                command = input("🗣️ > ")
                if command.lower() in ["exit", "quit"]:
                    self.do_exit(None)
                    break
                elif command.lower() == "help":
                    self.do_help(None)
                else:
                    self.execute_command(command)
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected. Type 'exit' to quit.")
            except EOFError:
                print("\nEOF detected. Exiting...")
                self.do_exit(None)
                break

    def execute_command(self, command: str) -> Tuple[bool, str]:
        """
        Execute a natural language command.

        Args:
            command: The natural language command to execute.

        Returns:
            Tuple of (success, output).
        """
        success, output = self.session.execute_natural_language(command)
        if success:
            print(f"Success: {output}")
        else:
            print(f"Error: {output}")
        return success, output

    def do_help(self, _):
        """Display help information."""
        print("\nPlainSpeak Help")
        print("==============")
        print("Enter commands in natural language, and PlainSpeak will translate them to shell commands.")
        print("Examples:")
        print("  list files in the current directory")
        print("  search for the word 'error' in log files")
        print("  create a new file called test.txt")
        print("\nSpecial commands:")
        print("  help - Display this help message")
        print("  exit, quit - Exit the REPL")

    def do_exit(self, _):
        """Exit the REPL."""
        print("Goodbye!")
        self.running = False
        return True

    def do_quit(self, _):
        """Alias for exit."""
        return self.do_exit(_)

    def print_welcome(self):
        """Print welcome message."""
        print("\nWelcome to PlainSpeak REPL!")
        print("Type your commands in plain English, and they will be translated to shell commands.")
        print("Type 'help' for a list of commands, or 'exit' to quit.\n")
