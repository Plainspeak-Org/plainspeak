"""Tests for the PlainSpeak interactive shell."""

import unittest
from unittest.mock import Mock, patch

from plainspeak.cli import PlainSpeakShell
from tests.test_cli.conftest import MockConsole, MockPanel, MockSyntax


class TestPlainSpeakShell(unittest.TestCase):
    """Test suite for the interactive shell."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_console = MockConsole()
        self.mock_prompt = Mock(return_value="")

    @patch("plainspeak.cli.NaturalLanguageParser")
    @patch("plainspeak.cli.Panel", MockPanel)
    @patch("plainspeak.cli.Syntax", MockSyntax)
    @patch("plainspeak.cli.console")
    @patch("plainspeak.cli.learning_store")
    def test_shell_translate_command_success(self, mock_learning_store, mock_console, mock_parser_class):
        """Test successful command translation in shell."""
        shell = PlainSpeakShell()
        shell.parser = Mock()
        shell.parser.parse.return_value = {"verb": "ls", "args": {"l": True}}
        mock_learning_store.add_command.return_value = 1  # Return a dummy command ID

        shell.onecmd("translate list files")

        # Check that output was formatted correctly
        mock_console.print.assert_called()
        args, kwargs = mock_console.print.call_args
        self.assertIsInstance(args[0], MockPanel)
        self.assertEqual(str(args[0]), "ls --l")
        self.assertEqual(kwargs.get("title"), "Generated Command")
        shell.parser.parse.assert_called_once()

    @patch("plainspeak.cli.NaturalLanguageParser")
    @patch("plainspeak.cli.Panel", MockPanel)
    @patch("plainspeak.cli.console")
    @patch("plainspeak.cli.learning_store")
    def test_shell_translate_command_failure(self, mock_learning_store, mock_console, mock_parser_class):
        """Test failed command translation in shell."""
        shell = PlainSpeakShell()
        shell.parser = Mock()
        shell.parser.parse.return_value = {}  # Empty result, which will trigger an error
        mock_learning_store.add_command.return_value = 1  # Return a dummy command ID

        shell.onecmd("translate do something impossible")

        # Check that an error panel was displayed
        mock_console.print.assert_called()
        args, kwargs = mock_console.print.call_args
        self.assertIsInstance(args[0], MockPanel)
        self.assertEqual(kwargs.get("title"), "Error")
        shell.parser.parse.assert_called_once()

    @patch("plainspeak.cli.NaturalLanguageParser")
    @patch("subprocess.run")
    @patch("plainspeak.cli.console")
    @patch("plainspeak.cli.learning_store")
    def test_shell_execute_command_success(
        self, mock_learning_store, mock_console, mock_subprocess_run, mock_parser_class
    ):
        """Test successful command execution in shell."""
        shell = PlainSpeakShell()
        mock_subprocess_run.return_value = Mock(stdout="test output\n", stderr="", returncode=0)

        result = shell.do_execute("ls -l")

        self.assertTrue(result)  # Should return True for success
        mock_subprocess_run.assert_called_once_with("ls -l", shell=True, check=False, capture_output=True, text=True)
        mock_console.print.assert_called_with("Command executed successfully", style="green")

    @patch("plainspeak.cli.NaturalLanguageParser")
    @patch("subprocess.run")
    @patch("plainspeak.cli.console")
    @patch("plainspeak.cli.learning_store")
    def test_shell_execute_command_failure(
        self, mock_learning_store, mock_console, mock_subprocess_run, mock_parser_class
    ):
        """Test command execution failure in shell."""
        shell = PlainSpeakShell()
        mock_subprocess_run.return_value = Mock(stdout="", stderr="Permission denied", returncode=1)

        result = shell.do_execute("cat /etc/shadow")

        self.assertFalse(result)  # Should return False for failure
        mock_subprocess_run.assert_called_once_with(
            "cat /etc/shadow", shell=True, check=False, capture_output=True, text=True
        )
        mock_console.print.assert_any_call("Command failed with exit code 1", style="red")

    @patch("plainspeak.cli.NaturalLanguageParser")
    @patch("plainspeak.cli.console")
    def test_shell_execute_empty_input(self, mock_console, mock_parser_class):
        """Test empty input handling for shell execute."""
        shell = PlainSpeakShell()

        result = shell.do_execute("")

        self.assertIsNone(result)  # Should return None for empty input
        mock_console.print.assert_called_with("Error: Empty input", style="red")

    def test_shell_default_handler(self):
        """Test default handler for unknown commands."""
        shell = PlainSpeakShell()
        shell.onecmd = Mock()  # Mock onecmd to check if it's called

        # Create a statement-like object with a raw attribute
        statement = Mock()
        statement.raw = "find large files"

        shell.default(statement)

        # Check that it redirects to translate
        shell.onecmd.assert_called_once_with("translate find large files")

    @patch("plainspeak.cli.PlainSpeakShell")
    def test_shell_command(self, mock_shell_class):
        """Test the shell command."""
        # Create a mock for shell instance and its cmdloop method
        mock_shell_instance = mock_shell_class.return_value
        mock_shell_instance.cmdloop = Mock()

        # Import the shell command function and call it
        from plainspeak.cli.commands import shell

        shell()

        # Verify that cmdloop was called
        mock_shell_instance.cmdloop.assert_called_once()
