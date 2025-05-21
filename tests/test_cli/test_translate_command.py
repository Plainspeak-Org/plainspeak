"""Tests for the translate command."""

import subprocess
import unittest
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from plainspeak.cli import app


class TestTranslateCommand(unittest.TestCase):
    """Test suite for the translate command."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_parser = Mock()
        self.mock_llm = Mock()

    @patch("plainspeak.cli.CommandParser")
    def test_translate_command_success(self, mock_command_parser_class):
        """Test successful command translation."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse.return_value = (True, "ls -l")

        result = self.runner.invoke(app, ["translate", "list files in detail"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Generated Command", result.stdout)
        self.assertIn("ls -l", result.stdout)
        mock_parser.parse.assert_called_once_with("list files in detail")

    @patch("plainspeak.cli.CommandParser")
    def test_translate_command_failure(self, mock_command_parser_class):
        """Test failed command translation."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse.return_value = (False, "ERROR: Invalid request")

        result = self.runner.invoke(app, ["translate", "do something impossible"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.stdout)
        self.assertIn("Invalid request", result.stdout)
        mock_parser.parse.assert_called_once_with("do something impossible")

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_success(self, mock_subprocess_run, mock_command_parser_class):
        """Test successful command translation and execution."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse.return_value = (True, "echo test")
        mock_subprocess_run.return_value = Mock(stdout="test output\n", stderr="", returncode=0)

        result = self.runner.invoke(app, ["translate", "--execute", "print test"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("test output", result.stdout)
        self.assertIn("Command executed successfully", result.stdout)
        mock_subprocess_run.assert_called_once_with(
            "echo test", shell=True, check=False, capture_output=True, text=True
        )
        mock_parser.parse.assert_called_once_with("print test")

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_command_error(self, mock_subprocess_run, mock_command_parser_class):
        """Test command execution failure handling."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse.return_value = (True, "invalid_command")
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")

        result = self.runner.invoke(app, ["translate", "--execute", "run invalid command"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error executing command", result.stdout)
        self.assertIn("Command failed", result.stdout)
        mock_parser.parse.assert_called_once_with("run invalid command")

    @patch("plainspeak.cli.CommandParser")
    @patch("subprocess.run")
    def test_translate_with_execute_non_zero_exit(self, mock_subprocess_run, mock_command_parser_class):
        """Test handling of commands that exit with non-zero status."""
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse.return_value = (True, "exit 1")
        mock_subprocess_run.return_value = Mock(stdout="", stderr="Some error occurred", returncode=1)

        result = self.runner.invoke(app, ["translate", "--execute", "fail command"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Command failed with exit code 1", result.stdout)
        self.assertIn("Some error occurred", result.stdout)
        mock_parser.parse.assert_called_once_with("fail command")

    @patch("plainspeak.cli.LLMInterface")  # Patch LLMInterface where CommandParser imports it
    def test_translate_cli_uses_default_parser_and_llm(self, mock_llm_interface):
        """Test that cli.translate uses default CommandParser and LLMInterface setup."""
        with patch(
            "plainspeak.cli.CommandParser.parse",
            return_value=(True, "ls"),
        ) as mock_parse:
            result = self.runner.invoke(app, ["translate", "list files"])

            self.assertEqual(result.exit_code, 0)
            mock_parse.assert_called_once_with("list files")
            mock_llm_interface.assert_called_once_with()

        help_result = self.runner.invoke(app, ["translate", "--help"])
        self.assertNotIn("--model", help_result.stdout)

    @patch("plainspeak.cli.CommandParser")
    def test_translate_empty_input(self, mock_command_parser_class):
        """Test handling of empty input to translate command."""
        result = self.runner.invoke(app, ["translate", ""])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: Empty input", result.stdout)
        mock_command_parser_class.return_value.parse.assert_not_called()
