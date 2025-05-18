"""
End-to-end tests for PlainSpeak.

This module tests the complete flow of PlainSpeak from natural language input to command execution,
including plugin matching, command generation, and execution.
"""

import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from plainspeak.cli.repl import REPLInterface
from plainspeak.core.executor import CommandExecutor
from plainspeak.core.llm import LLMInterface
from plainspeak.core.parser import NaturalLanguageParser
from plainspeak.core.session import Session
from plainspeak.plugins.manager import PluginManager


class TestEndToEnd(unittest.TestCase):
    """
    End-to-end tests for PlainSpeak.

    These tests cover the complete flow from natural language input to command execution.
    """

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for file operations
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create a mock LLM interface that always returns a specific result
        self.mock_llm = MagicMock(spec=LLMInterface)

        # Create a parser with the mock LLM
        self.parser = NaturalLanguageParser(llm=self.mock_llm)

        # Create a plugin manager
        self.plugin_manager = PluginManager()

        # Create a command executor that doesn't actually execute commands
        self.mock_executor = MagicMock(spec=CommandExecutor)
        self.mock_executor.execute.return_value = (
            True,
            "Command executed successfully",
        )

        # Create a session
        self.session = Session(
            parser=self.parser,
            plugin_manager=self.plugin_manager,
            executor=self.mock_executor,
            working_dir=str(self.test_dir),
        )

        # Create a REPL interface that doesn't require actual input
        self.repl = REPLInterface(session=self.session)

        # Configure the mock LLM responses for different queries
        self.setup_mock_llm_responses()

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def setup_mock_llm_responses(self):
        """Configure mock LLM responses for different types of queries."""
        # Map natural language queries to parsed results (verb and args)
        responses = {
            "list files in the current directory": {
                "verb": "ls",
                "args": {"path": "."},
            },
            "find all text files": {
                "verb": "find",
                "args": {"path": ".", "pattern": "*.txt"},
            },
            "create a file named test.txt": {
                "verb": "create",
                "args": {"file": "test.txt"},
            },
            "show running processes": {"verb": "ps", "args": {}},
            "search for the word error in log files": {
                "verb": "grep",
                "args": {"pattern": "error", "path": "*.log"},
            },
        }

        # Configure the mock to return appropriate responses
        def mock_parse_side_effect(text):
            if text in responses:
                return responses[text]
            # Default fallback for unknown queries
            return {"verb": None, "args": {}}

        self.mock_llm.parse_natural_language.side_effect = mock_parse_side_effect

    def test_file_operations(self):
        """Test file operations commands end-to-end."""
        # Test listing files
        self.plugin_manager.generate_command = Mock(return_value=(True, "ls -la ."))

        # Execute the command through the session
        result = self.session.execute_natural_language("list files in the current directory")

        # Verify the flow worked correctly
        self.assertTrue(result[0])  # Success flag
        self.assertEqual(result[1], "Command executed successfully")

        # Verify the right plugin was used and the command was generated correctly
        self.mock_llm.parse_natural_language.assert_called_with("list files in the current directory")
        self.plugin_manager.generate_command.assert_called_with("ls", {"path": "."})
        self.mock_executor.execute.assert_called_with("ls -la .")

    def test_search_operations(self):
        """Test search operations commands end-to-end."""
        # Test searching for files
        self.plugin_manager.generate_command = Mock(return_value=(True, "find . -name '*.txt'"))

        # Execute the command through the session
        result = self.session.execute_natural_language("find all text files")

        # Verify the flow worked correctly
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Command executed successfully")

        # Verify the right plugin was used and the command was generated correctly
        self.mock_llm.parse_natural_language.assert_called_with("find all text files")
        self.plugin_manager.generate_command.assert_called_with("find", {"path": ".", "pattern": "*.txt"})
        self.mock_executor.execute.assert_called_with("find . -name '*.txt'")

    def test_create_operations(self):
        """Test file creation commands end-to-end."""
        # Test creating a file
        self.plugin_manager.generate_command = Mock(return_value=(True, "touch test.txt"))

        # Execute the command through the session
        result = self.session.execute_natural_language("create a file named test.txt")

        # Verify the flow worked correctly
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Command executed successfully")

        # Verify the right plugin was used and the command was generated correctly
        self.mock_llm.parse_natural_language.assert_called_with("create a file named test.txt")
        self.plugin_manager.generate_command.assert_called_with("create", {"file": "test.txt"})
        self.mock_executor.execute.assert_called_with("touch test.txt")

    def test_system_operations(self):
        """Test system operations commands end-to-end."""
        # Test checking running processes
        self.plugin_manager.generate_command = Mock(return_value=(True, "ps aux"))

        # Execute the command through the session
        result = self.session.execute_natural_language("show running processes")

        # Verify the flow worked correctly
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Command executed successfully")

        # Verify the right plugin was used and the command was generated correctly
        self.mock_llm.parse_natural_language.assert_called_with("show running processes")
        self.plugin_manager.generate_command.assert_called_with("ps", {})
        self.mock_executor.execute.assert_called_with("ps aux")

    def test_text_operations(self):
        """Test text operations commands end-to-end."""
        # Test searching in files
        self.plugin_manager.generate_command = Mock(return_value=(True, "grep -r 'error' *.log"))

        # Execute the command through the session
        result = self.session.execute_natural_language("search for the word error in log files")

        # Verify the flow worked correctly
        self.assertTrue(result[0])
        self.assertEqual(result[1], "Command executed successfully")

        # Verify the right plugin was used and the command was generated correctly
        self.mock_llm.parse_natural_language.assert_called_with("search for the word error in log files")
        self.plugin_manager.generate_command.assert_called_with("grep", {"pattern": "error", "path": "*.log"})
        self.mock_executor.execute.assert_called_with("grep -r 'error' *.log")

    def test_unknown_command(self):
        """Test handling of unknown commands."""
        # Setup for unknown command
        self.plugin_manager.generate_command = Mock(return_value=(False, "No plugin found for verb: unknown"))
        self.mock_llm.parse_natural_language.return_value = {
            "verb": "unknown",
            "args": {},
        }

        # Execute the command through the session
        result = self.session.execute_natural_language("do something completely unknown")

        # Verify that the error was properly handled
        self.assertFalse(result[0])
        self.assertEqual(result[1], "No plugin found for verb: unknown")

    def test_command_execution_error(self):
        """Test handling of command execution errors."""
        # Setup command generation success but execution failure
        self.plugin_manager.generate_command = Mock(return_value=(True, "invalid_command"))
        self.mock_executor.execute.return_value = (
            False,
            "Command not found: invalid_command",
        )

        # Execute the command through the session
        result = self.session.execute_natural_language("run an invalid command")

        # Verify that the error was properly handled
        self.assertFalse(result[0])
        self.assertEqual(result[1], "Command not found: invalid_command")


class TestREPLEndToEnd(unittest.TestCase):
    """
    End-to-end tests for PlainSpeak REPL interface.

    These tests validate the REPL interface with simulated user input.
    """

    def setUp(self):
        """Set up test environment."""
        # Create a mock session
        self.mock_session = MagicMock(spec=Session)
        self.mock_session.execute_natural_language.return_value = (
            True,
            "Command executed successfully",
        )

        # Create a REPL with the mock session
        self.repl = REPLInterface(session=self.mock_session)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("sys.stdin")
    def test_repl_execution(self, mock_stdin, mock_stdout):
        """Test REPL execution with mocked input/output."""
        # Setup input sequence: command, help, exit
        mock_stdin.readline.side_effect = ["list files\n", "help\n", "exit\n"]

        # Setup successful command execution
        self.mock_session.execute_natural_language.return_value = (True, "ls -la")

        # Call the REPL's cmdloop method
        # This should process the three inputs and then exit
        with patch.object(self.repl, "cmdloop", return_value=None) as mock_cmdloop:
            self.repl.run()
            mock_cmdloop.assert_called_once()

        # Verify the session was called correctly
        self.mock_session.execute_natural_language.assert_called_with("list files")

    @patch("sys.stdout", new_callable=StringIO)
    def test_repl_help(self, mock_stdout):
        """Test REPL help command."""
        # Call the help method directly
        self.repl.do_help(None)

        # Verify help output
        output = mock_stdout.getvalue()
        self.assertIn("PlainSpeak Help", output)

    def test_repl_exit(self):
        """Test REPL exit command."""
        # The exit method should return True to signal exit
        result = self.repl.do_exit(None)
        self.assertTrue(result)

        # Test aliases
        result = self.repl.do_quit(None)
        self.assertTrue(result)


class TestIntegrationWithMockedCommands(unittest.TestCase):
    """
    Integration tests with mocked command execution.

    These tests use the real parser, plugin manager, and plugin instances,
    but mock the actual command execution.
    """

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create some test files
        (self.test_dir / "test.txt").write_text("This is a test file.")
        (self.test_dir / "another.txt").write_text("This is another test file.")
        (self.test_dir / "data.csv").write_text("id,name\n1,test\n2,another")

        # Create a mock executor that logs commands but doesn't execute them
        self.mock_executor = MagicMock(spec=CommandExecutor)
        self.mock_executor.execute.return_value = (
            True,
            "Command executed successfully",
        )

        # Create a real plugin manager
        self.plugin_manager = PluginManager()

        # Create a real parser with a mock LLM
        self.mock_llm = MagicMock(spec=LLMInterface)
        self.parser = NaturalLanguageParser(llm=self.mock_llm)

        # Create a session with the real components and mock executor
        self.session = Session(
            parser=self.parser,
            plugin_manager=self.plugin_manager,
            executor=self.mock_executor,
            working_dir=str(self.test_dir),
        )

        # Configure the mock LLM
        self.configure_mock_llm()

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def configure_mock_llm(self):
        """Configure the mock LLM with realistic responses."""
        # Map queries to realistic parser results
        responses = {
            "list all text files": {
                "verb": "find",
                "args": {"path": ".", "pattern": "*.txt"},
            },
            "show the contents of test.txt": {
                "verb": "read",
                "args": {"file": "test.txt"},
            },
            "search for the word test in all files": {
                "verb": "grep",
                "args": {"pattern": "test", "path": "."},
            },
            "create a file called output.txt": {
                "verb": "create",
                "args": {"file": "output.txt"},
            },
            "copy test.txt to backup.txt": {
                "verb": "copy",
                "args": {"source": "test.txt", "destination": "backup.txt"},
            },
            "delete backup.txt": {"verb": "delete", "args": {"file": "backup.txt"}},
        }

        # Configure the mock LLM
        def mock_parse_side_effect(text):
            if text in responses:
                return responses[text]
            # Use a simple heuristic for unknown queries
            words = text.lower().split()
            if "list" in words or "show" in words:
                return {"verb": "ls", "args": {"path": "."}}
            elif "search" in words or "find" in words:
                return {"verb": "grep", "args": {"pattern": "test", "path": "."}}
            elif "create" in words:
                return {"verb": "create", "args": {"file": "output.txt"}}
            elif "copy" in words:
                return {
                    "verb": "copy",
                    "args": {"source": "test.txt", "destination": "backup.txt"},
                }
            elif "delete" in words or "remove" in words:
                return {"verb": "delete", "args": {"file": "backup.txt"}}
            else:
                return {"verb": None, "args": {}}

        self.mock_llm.parse_natural_language.side_effect = mock_parse_side_effect

    def test_find_files(self):
        """Test finding files by pattern."""
        # Execute the command
        result = self.session.execute_natural_language("list all text files")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("find", cmd)
        self.assertIn("*.txt", cmd)

    def test_read_file(self):
        """Test reading file contents."""
        # Execute the command
        result = self.session.execute_natural_language("show the contents of test.txt")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("test.txt", cmd)

    def test_search_in_files(self):
        """Test searching in files."""
        # Execute the command
        result = self.session.execute_natural_language("search for the word test in all files")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("grep", cmd)
        self.assertIn("test", cmd)

    def test_create_file(self):
        """Test creating a file."""
        # Execute the command
        result = self.session.execute_natural_language("create a file called output.txt")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("output.txt", cmd)

    def test_copy_file(self):
        """Test copying a file."""
        # Execute the command
        result = self.session.execute_natural_language("copy test.txt to backup.txt")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("test.txt", cmd)
        self.assertIn("backup.txt", cmd)

    def test_delete_file(self):
        """Test deleting a file."""
        # Execute the command
        result = self.session.execute_natural_language("delete backup.txt")

        # Verify the command was generated and executed correctly
        self.assertTrue(result[0])
        self.mock_executor.execute.assert_called()
        cmd = self.mock_executor.execute.call_args[0][0]
        self.assertIn("backup.txt", cmd)


if __name__ == "__main__":
    unittest.main()
