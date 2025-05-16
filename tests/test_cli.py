"""
Tests for the CLI module.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from typer.testing import CliRunner
from cmd2 import CommandResult

from plainspeak.cli import app, PlainSpeakShell, translate, shell

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

class TestCLI(unittest.TestCase):
    """Test suite for the CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.mock_parser = Mock()
        self.mock_llm = Mock()

    @patch('plainspeak.cli.CommandParser')
    def test_translate_command_success(self, mock_command_parser_class):
        """Test successful command translation."""
        # Set up mock parser to return a successful result
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "ls -l")

        # Run the command
        result = self.runner.invoke(app, ["translate", "list files in detail"])
        
        # Check the result
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Generated Command", result.stdout)
        self.assertIn("ls -l", result.stdout)

    @patch('plainspeak.cli.CommandParser')
    def test_translate_command_failure(self, mock_command_parser_class):
        """Test failed command translation."""
        # Set up mock parser to return an error
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (False, "ERROR: Invalid request")

        # Run the command
        result = self.runner.invoke(app, ["translate", "do something impossible"])
        
        # Check the result
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error", result.stdout)
        self.assertIn("Invalid request", result.stdout)

    @patch('plainspeak.cli.CommandParser')
    @patch('subprocess.run') # Changed from os.system to subprocess.run
    def test_translate_with_execute(self, mock_subprocess_run, mock_command_parser_class):
        """Test command translation with execution."""
        # Set up mock parser to return a successful result
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "echo test")
        
        # Mock subprocess.run to return a successful process
        mock_subprocess_run.return_value = Mock(stdout="test output", stderr="", returncode=0)

        # Run the command with execute flag
        result = self.runner.invoke(app, ["translate", "--execute", "print test"])
        
        # Check the result
        self.assertEqual(result.exit_code, 0)
        mock_subprocess_run.assert_called_once_with(
            "echo test", shell=True, check=False, capture_output=True, text=True
        )

    @patch('plainspeak.cli.CommandParser')
    def test_translate_with_custom_model(self, mock_command_parser_class):
        """Test command translation with custom model path."""
        # Set up mock parser
        mock_parser = mock_command_parser_class.return_value
        mock_parser.parse_to_command.return_value = (True, "ls")

        # Run the command with model path
        result = self.runner.invoke(
            app,
            ["translate", "--model", "custom/model.gguf", "list files"]
        )
        
        # Check the result
        self.assertEqual(result.exit_code, 0)
        # Verify that CommandParser was called with a custom LLM
        mock_command_parser_class.assert_called_once()
        call_kwargs = mock_command_parser_class.call_args[1]
        self.assertIsNotNone(call_kwargs.get('llm'))

class TestPlainSpeakShell(unittest.TestCase):
    """Test suite for the interactive shell."""

    @patch('plainspeak.cli.CommandParser')
    def setUp(self, mock_command_parser_class):
        """Set up test fixtures."""
        # Configure the mock parser that will be used by PlainSpeakShell
        self.mock_parser = Mock()
        mock_command_parser_class.return_value = self.mock_parser
        
        # Now create the shell, which will use our mocked parser
        self.shell = PlainSpeakShell()

    @patch('plainspeak.cli.Panel', MockPanel)
    @patch('plainspeak.cli.Syntax', MockSyntax)
    def test_translate_command_success(self):
        """Test successful command translation in shell."""
        self.shell.parser.parse_to_command.return_value = (True, "ls -l")
        
        with patch('plainspeak.cli.console.print') as mock_print:
            self.shell.onecmd('translate list files')
            mock_print.assert_called()
            
            # The print should have been called with a Panel containing a Syntax object
            # that contains our command
            panel = mock_print.call_args[0][0]
            self.assertIsInstance(panel, MockPanel)
            self.assertIsInstance(panel.content, MockSyntax)
            self.assertEqual(str(panel.content), "ls -l")
            self.assertEqual(panel.kwargs.get('title'), "Generated Command")

    @patch('plainspeak.cli.Panel', MockPanel)
    def test_translate_command_failure(self):
        """Test failed command translation in shell."""
        error_msg = "ERROR: Invalid command"
        self.shell.parser.parse_to_command.return_value = (False, error_msg)
        
        with patch('plainspeak.cli.console.print') as mock_print:
            self.shell.onecmd('translate invalid command')
            mock_print.assert_called()
            
            # The print should have been called with a Panel containing our error message
            panel = mock_print.call_args[0][0]
            self.assertIsInstance(panel, MockPanel)
            self.assertEqual(str(panel.content), error_msg)
            self.assertEqual(panel.kwargs.get('title'), "Error")

    @patch('subprocess.run')
    def test_execute_command(self, mock_subprocess_run):
        """Test command execution in shell."""
        # Mock subprocess.run to return a successful process
        mock_subprocess_run.return_value = Mock(stdout="test output", stderr="", returncode=0)

        # Test empty command
        with patch('plainspeak.cli.console.print') as mock_print:
            self.shell.onecmd('translate -e ""') # "" will be stripped to empty
            mock_print.assert_any_call("Error: Empty input", style="red")
            self.assertFalse(mock_subprocess_run.called)
            
        # Test successful execution
        mock_subprocess_run.reset_mock()
        self.shell.parser.parse_to_command.return_value = (True, "echo test")
        with patch('plainspeak.cli.console.print'):
            self.shell.onecmd('translate -e print test')
            mock_subprocess_run.assert_called_once_with(
                "echo test", shell=True, check=False, capture_output=True, text=True
            )

        # Test command with only whitespace (should not execute)
        mock_subprocess_run.reset_mock()
        self.shell.parser.parse_to_command.return_value = (True, "   ")
        with patch('plainspeak.cli.console.print'):
            self.shell.onecmd('translate -e blank') # 'blank' is the input, parser returns '   '
            self.assertFalse(mock_subprocess_run.called)

    def test_default_handler(self):
        """Test that unknown commands are treated as natural language input."""
        self.shell.parser.parse_to_command.return_value = (True, "ls")
        
        with patch('plainspeak.cli.console.print'):
            self.shell.onecmd('show me the files')  # This should be handled by default()
            self.shell.parser.parse_to_command.assert_called_once()
