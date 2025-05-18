"""
Tests for the CLI module.
"""

import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from plainspeak.cli import PlainSpeakShell, app, main


# Mock classes for Rich components
class MockPanel:
    def __init__(self, content, **kwargs):
        self.content = content
        self.kwargs = kwargs

    def __str__(self):
        return str(self.content)


class MockSyntax:
    def __init__(self, content, *args, **kwargs):
        self.content = content

    def __str__(self):
        return str(self.content)


class MockPrompt:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.default_value = kwargs.get("default", "")

    def __call__(self, *args, **kwargs):
        return self.default_value


# Mock high-level Rich components
class MockConsole:
    def __init__(self):
        self.printed = []
        self.prompted = []

    def print(self, *args, **kwargs):
        self.printed.append((args, kwargs))

    def input(self, *args, **kwargs):
        self.prompted.append((args, kwargs))
        return ""


class TestCLI(unittest.TestCase):
    """Test suite for the CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_parser = Mock()
        self.mock_llm = Mock()

    @patch("plainspeak.cli.CommandParser")
    def test_translate_command_success(self, mock_command_parser_class):
        """Test successful command translation."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "ls -l")

        result = self.runner.invoke(app, ["translate", "list files in detail"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Generated Command", result.stdout)
        self.assertIn("ls -l", result.stdout)

    @patch("plainspeak.cli.CommandParser")
    def test_translate_command_failure(self, mock_command_parser_class):
        """Test failed command translation."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (False, "ERROR: Invalid request")

        result = self.runner.invoke(app, ["translate", "do something impossible"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.stdout)
        self.assertIn("Invalid request", result.stdout)

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_success(self, mock_subprocess_run, mock_command_parser_class):
        """Test successful command translation and execution."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "echo test")
        mock_subprocess_run.return_value = Mock(stdout="test output\n", stderr="", returncode=0)

        result = self.runner.invoke(app, ["translate", "--execute", "print test"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("test output", result.stdout)
        self.assertIn("Command executed successfully", result.stdout)
        mock_subprocess_run.assert_called_once_with(
            "echo test", shell=True, check=False, capture_output=True, text=True
        )

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_command_error(self, mock_subprocess_run, mock_command_parser_class):
        """Test command execution failure handling."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "invalid_command")
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")

        result = self.runner.invoke(app, ["translate", "--execute", "run invalid command"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error executing command", result.stdout)
        self.assertIn("Command failed", result.stdout)

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_non_zero_exit(self, mock_subprocess_run, mock_command_parser_class):
        """Test handling of commands that exit with non-zero status."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "exit 1")
        mock_subprocess_run.return_value = Mock(stdout="", stderr="Some error occurred", returncode=1)

        result = self.runner.invoke(app, ["translate", "--execute", "fail command"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Command failed with exit code 1", result.stdout)
        self.assertIn("Some error occurred", result.stdout)

    @patch("plainspeak.parser.LLMInterface")  # Patch LLMInterface where CommandParser imports it
    def test_translate_cli_uses_default_parser_and_llm(self, mock_llm_interface_in_parser_module):
        """Test that cli.translate uses default CommandParser and LLMInterface setup."""
        with patch(
            "plainspeak.parser.CommandParser.parse_to_command",
            return_value=(True, "ls"),
        ) as mock_parse_to_command:
            result = self.runner.invoke(app, ["translate", "list files"])

            self.assertEqual(result.exit_code, 0)
            mock_parse_to_command.assert_called_once_with("list files")
            mock_llm_interface_in_parser_module.assert_called_once_with()

        help_result = self.runner.invoke(app, ["translate", "--help"])
        self.assertNotIn("--model", help_result.stdout)

    @patch("plainspeak.cli.CommandParser")
    def test_translate_empty_input(self, mock_command_parser_class):
        """Test handling of empty input to translate command."""
        result = self.runner.invoke(app, ["translate", ""])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: Empty input", result.stdout)
        mock_command_parser_class.return_value.parse_to_command.assert_not_called()


class TestPlainSpeakShell(unittest.TestCase):
    """Test suite for the interactive shell."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_console = MockConsole()
        self.mock_prompt = MockPrompt()

    @patch("plainspeak.cli.CommandParser")
    @patch("plainspeak.cli.Panel", MockPanel)
    @patch("plainspeak.cli.Syntax", MockSyntax)
    @patch("plainspeak.cli.console")
    def test_shell_translate_command_success(self, mock_console, mock_command_parser_class):
        """Test successful command translation in shell."""
        shell = PlainSpeakShell()
        shell.parser.parse_to_command.return_value = (True, "ls -l")

        shell.onecmd("translate list files")

        # Check that output was formatted correctly
        last_print = mock_console.print.call_args[0][0]
        self.assertIsInstance(last_print, MockPanel)
        self.assertEqual(str(last_print.content), "ls -l")
        self.assertEqual(last_print.kwargs.get("title"), "Generated Command")

    @patch("plainspeak.cli.CommandParser")
    @patch("plainspeak.cli.Panel", MockPanel)
    @patch("plainspeak.cli.console")
    def test_shell_translate_command_failure(self, mock_console, mock_command_parser_class):
        """Test failed command translation in shell."""
        shell = PlainSpeakShell()
        error_msg = "ERROR: Invalid command"
        shell.parser.parse_to_command.return_value = (False, error_msg)

        shell.onecmd("translate invalid command")

        last_print = mock_console.print.call_args[0][0]
        self.assertIsInstance(last_print, MockPanel)
        self.assertEqual(str(last_print.content), error_msg)
        self.assertEqual(last_print.kwargs.get("title"), "Error")

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    @patch("plainspeak.cli.console")
    def test_shell_execute_command_success(self, mock_console, mock_subprocess_run, mock_command_parser_class):
        """Test successful command execution in shell."""
        shell = PlainSpeakShell()
        shell.parser.parse_to_command.return_value = (True, "echo test")
        mock_subprocess_run.return_value = Mock(stdout="test output\n", stderr="", returncode=0)

        shell.onecmd("translate -e print test")

        mock_subprocess_run.assert_called_once_with(
            "echo test", shell=True, check=False, capture_output=True, text=True
        )
        mock_console.print.assert_any_call("Command executed successfully", style="green")

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    @patch("plainspeak.cli.console")
    def test_shell_execute_command_failure(self, mock_console, mock_subprocess_run, mock_command_parser_class):
        """Test command execution failure in shell."""
        shell = PlainSpeakShell()
        shell.parser.parse_to_command.return_value = (True, "invalid_command")
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")

        shell.onecmd("translate -e fail command")

        mock_console.print.assert_any_call("Error executing command: Command failed", style="red")

    @patch("plainspeak.cli.CommandParser")
    @patch("plainspeak.cli.console")
    def test_shell_execute_empty_input(self, mock_console, mock_command_parser_class):
        """Test handling of empty input in shell execute command."""
        shell = PlainSpeakShell()

        shell.onecmd('translate -e ""')
        mock_console.print.assert_any_call("Error: Empty input", style="red")
        shell.parser.parse_to_command.assert_not_called()

    def test_shell_default_handler(self):
        """Test that unknown commands are treated as natural language input."""
        with patch("plainspeak.cli.CommandParser") as mock_command_parser_class:
            # Mock the command parser
            mock_parser = Mock()
            mock_parser.parse_to_command.return_value = (True, "ls")
            mock_command_parser_class.return_value = mock_parser

            # Create shell and mock console output
            shell = PlainSpeakShell()
            shell.parser = mock_parser  # Replace the parser with our mock

            # Create a mock Statement object
            mock_statement = Mock()
            mock_statement.raw = "show me the files"
            mock_statement.__str__ = lambda x: "show me the files"

            # Test the default handler
            shell.default(mock_statement)
            mock_parser.parse_to_command.assert_called_once_with("show me the files")

    @patch("plainspeak.cli.PlainSpeakShell")
    def test_shell_command(self, mock_shell_class):
        """Test the shell command that starts interactive mode."""
        # Mock the cmdloop method
        mock_shell_instance = mock_shell_class.return_value
        mock_shell_instance.cmdloop.return_value = None

        result = self.runner.invoke(app, ["shell"])

        self.assertEqual(result.exit_code, 0)
        mock_shell_class.assert_called_once()
        mock_shell_instance.cmdloop.assert_called_once()

    @patch("plainspeak.cli.app")
    def test_main_function(self, mock_app):
        """Test the main entry point function."""
        # Test with no arguments (should show help)
        sys.argv = ["plainspeak"]
        main()
        mock_app.assert_called_once()

        # Test with command
        mock_app.reset_mock()
        sys.argv = ["plainspeak", "translate", "list files"]
        main()
        mock_app.assert_called_once()


if __name__ == "__main__":
    unittest.main()
