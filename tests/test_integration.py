"""
Integration tests for PlainSpeak.

This module contains integration tests that verify the interaction between
different components of PlainSpeak, particularly the parser, plugin manager,
and command execution pipeline.
"""

import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Tuple
from unittest.mock import MagicMock

from plainspeak.core.executor import CommandExecutor
from plainspeak.core.llm import LLMInterface
from plainspeak.core.parser import NaturalLanguageParser
from plainspeak.core.session import Session
from plainspeak.plugins.base import PluginRegistry
from plainspeak.plugins.file import FilePlugin
from plainspeak.plugins.manager import PluginManager
from plainspeak.plugins.network import NetworkPlugin
from plainspeak.plugins.system import SystemPlugin
from plainspeak.plugins.text import TextPlugin


class TestCommandPipeline(unittest.TestCase):
    """
    Test the command generation and execution pipeline.

    These tests focus on the interaction between the parser, plugin manager,
    and command executor.
    """

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create test files
        (self.test_dir / "test.txt").write_text("This is a test file")
        (self.test_dir / "log.txt").write_text("INFO: Test log entry\nERROR: Something went wrong")

        # Create a directory to cd into
        self.sub_dir = self.test_dir / "subdir"
        self.sub_dir.mkdir()
        (self.sub_dir / "subfile.txt").write_text("File in subdirectory")

        # Create mock LLM
        self.mock_llm = MagicMock(spec=LLMInterface)

        # Set up the plugin registry with real plugins
        self.registry = PluginRegistry()
        self.registry.register(FilePlugin())
        self.registry.register(TextPlugin())
        self.registry.register(SystemPlugin())
        self.registry.register(NetworkPlugin())

        # Create plugin manager with the registry
        self.plugin_manager = PluginManager()
        self.plugin_manager.registry = self.registry

        # Create a mock executor that records commands but doesn't execute them
        self.mock_executor = MagicMock(spec=CommandExecutor)
        self.mock_executor.execute.return_value = (
            True,
            "Command executed successfully",
        )

        # Create a parser with mock LLM
        self.parser = NaturalLanguageParser(llm=self.mock_llm)

        # Create a session
        self.session = Session(
            parser=self.parser,
            plugin_manager=self.plugin_manager,
            executor=self.mock_executor,
            working_dir=str(self.test_dir),
        )

        # Configure mock LLM responses
        self.setup_mock_llm()

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def setup_mock_llm(self):
        """Set up mock LLM responses for different queries."""
        # Define sample queries and their expected parsed outputs
        self.llm_responses = {
            "list files": {"verb": "ls", "args": {"path": "."}},
            "find all txt files": {
                "verb": "find",
                "args": {"path": ".", "pattern": "*.txt"},
            },
            "search for ERROR in log.txt": {
                "verb": "grep",
                "args": {"pattern": "ERROR", "file": "log.txt"},
            },
            "show processes": {"verb": "ps", "args": {}},
            "ping google.com": {"verb": "ping", "args": {"host": "google.com"}},
            "create a file called newfile.txt": {
                "verb": "create",
                "args": {"file": "newfile.txt"},
            },
            "copy test.txt to backup.txt": {
                "verb": "copy",
                "args": {"source": "test.txt", "destination": "backup.txt"},
            },
            "move test.txt to archive/": {
                "verb": "move",
                "args": {"source": "test.txt", "destination": "archive/"},
            },
            "delete backup.txt": {"verb": "delete", "args": {"file": "backup.txt"}},
            "download https://example.com/file.txt": {
                "verb": "wget",
                "args": {"url": "https://example.com/file.txt"},
            },
            "change directory to subdir": {"verb": "cd", "args": {"path": "subdir"}},
            "show disk usage": {"verb": "df", "args": {}},
        }

        # Configure the mock
        def mock_parse(query: str) -> Dict[str, Any]:
            if query in self.llm_responses:
                return self.llm_responses[query]

            # Simple fallback for unknown queries
            words = query.lower().split()
            if "list" in words or "show" in words:
                return {"verb": "ls", "args": {"path": "."}}
            elif "search" in words or "find" in words:
                return {"verb": "grep", "args": {"pattern": "test", "path": "."}}
            elif "create" in words:
                return {"verb": "create", "args": {"file": "output.txt"}}
            else:
                return {"verb": None, "args": {}}

        self.mock_llm.parse_natural_language.side_effect = mock_parse

    def run_command(self, query: str) -> Tuple[bool, str, str]:
        """
        Run a command and return the results.

        Args:
            query: The natural language query.

        Returns:
            Tuple of (success, command, output).
        """
        # Configure mock executor to track the command
        command_tracked = [None]

        def track_command(cmd: str) -> Tuple[bool, str]:
            command_tracked[0] = cmd
            return (True, f"Executed: {cmd}")

        self.mock_executor.execute.side_effect = track_command

        # Execute the command
        success, output = self.session.execute_natural_language(query)

        return success, command_tracked[0], output

    def test_file_listing(self):
        """Test file listing commands."""
        success, command, output = self.run_command("list files")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("ls", command)

        # Verify the parser was called with the right query
        self.mock_llm.parse_natural_language.assert_called_with("list files")

    def test_file_search(self):
        """Test file search commands."""
        success, command, output = self.run_command("find all txt files")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("find", command)
        self.assertIn("*.txt", command)

    def test_text_search(self):
        """Test text search commands."""
        success, command, output = self.run_command("search for ERROR in log.txt")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("grep", command)
        self.assertIn("ERROR", command)
        self.assertIn("log.txt", command)

    def test_system_commands(self):
        """Test system commands."""
        success, command, output = self.run_command("show processes")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("ps", command)

    def test_network_commands(self):
        """Test network commands."""
        success, command, output = self.run_command("ping google.com")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("ping", command)
        self.assertIn("google.com", command)

    def test_file_creation(self):
        """Test file creation commands."""
        success, command, output = self.run_command("create a file called newfile.txt")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("newfile.txt", command)

    def test_file_copying(self):
        """Test file copying commands."""
        success, command, output = self.run_command("copy test.txt to backup.txt")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("test.txt", command)
        self.assertIn("backup.txt", command)

    def test_file_moving(self):
        """Test file moving commands."""
        success, command, output = self.run_command("move test.txt to archive/")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("test.txt", command)
        self.assertIn("archive/", command)

    def test_file_deletion(self):
        """Test file deletion commands."""
        success, command, output = self.run_command("delete backup.txt")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("backup.txt", command)

    def test_directory_navigation(self):
        """Test directory navigation commands."""
        success, command, output = self.run_command("change directory to subdir")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("cd", command)
        self.assertIn("subdir", command)

    def test_disk_usage(self):
        """Test disk usage commands."""
        success, command, output = self.run_command("show disk usage")

        # Verify command generation
        self.assertTrue(success)
        self.assertIn("df", command)

    def test_command_failure(self):
        """Test handling of command failure."""
        # Configure executor to return failure
        self.mock_executor.execute.side_effect = lambda cmd: (
            False,
            f"Error: {cmd} failed",
        )

        # Run command
        success, output = self.session.execute_natural_language("list files")

        # Verify error handling
        self.assertFalse(success)
        self.assertIn("Error", output)

    def test_unknown_verb(self):
        """Test handling of unknown verbs."""
        # Configure LLM to return unknown verb
        self.mock_llm.parse_natural_language.return_value = {
            "verb": "unknown_verb",
            "args": {},
        }

        # Run command
        success, output = self.session.execute_natural_language("do something unknown")

        # Verify error handling
        self.assertFalse(success)
        self.assertIn("No plugin found for verb", output)


class TestLearningSystem(unittest.TestCase):
    """
    Test the learning system that improves command generation over time.

    These tests verify that the system learns from feedback and improves
    command generation accuracy.
    """

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "learning.db"

        # Create mock components
        self.mock_llm = MagicMock(spec=LLMInterface)
        self.plugin_manager = PluginManager()
        self.mock_executor = MagicMock(spec=CommandExecutor)

        # Create a parser with mock LLM
        self.parser = NaturalLanguageParser(llm=self.mock_llm)

        # Create a session
        self.session = Session(
            parser=self.parser,
            plugin_manager=self.plugin_manager,
            executor=self.mock_executor,
            working_dir=str(self.temp_dir.name),
        )

        # Initialize learning database
        self.session.init_learning_database(str(self.db_path))

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_feedback_storage(self):
        """Test that feedback is stored in the database."""
        # Configure mocks for a successful command
        self.mock_llm.parse_natural_language.return_value = {
            "verb": "ls",
            "args": {"path": "."},
        }
        self.plugin_manager.generate_command.return_value = (True, "ls -la .")
        self.mock_executor.execute.return_value = (True, "file1\nfile2")

        # Execute a command
        query = "list files"
        success, output = self.session.execute_natural_language(query)

        # Provide feedback that the command was good
        self.session.record_feedback(query, True)

        # Verify the feedback was recorded
        feedback_data = self.session.get_feedback_for_query(query)
        self.assertIsNotNone(feedback_data)
        self.assertTrue(feedback_data["positive"])

    def test_negative_feedback(self):
        """Test that negative feedback is stored correctly."""
        # Configure mocks for a successful command
        self.mock_llm.parse_natural_language.return_value = {
            "verb": "ls",
            "args": {"path": "."},
        }
        self.plugin_manager.generate_command.return_value = (True, "ls -la .")
        self.mock_executor.execute.return_value = (True, "file1\nfile2")

        # Execute a command
        query = "show directory"
        success, output = self.session.execute_natural_language(query)

        # Provide feedback that the command was not what the user wanted
        self.session.record_feedback(query, False)

        # Verify the feedback was recorded
        feedback_data = self.session.get_feedback_for_query(query)
        self.assertIsNotNone(feedback_data)
        self.assertFalse(feedback_data["positive"])

    def test_learning_from_feedback(self):
        """Test that the system learns from feedback."""
        # First execution - uses default verb
        self.mock_llm.parse_natural_language.return_value = {
            "verb": "ls",
            "args": {"path": "."},
        }
        self.plugin_manager.generate_command.return_value = (True, "ls -la .")
        self.mock_executor.execute.return_value = (True, "file1\nfile2")

        query = "show directory contents"
        self.session.execute_natural_language(query)

        # Provide negative feedback
        self.session.record_feedback(query, False)

        # Record corrected command
        corrected_command = "find . -type f | sort"
        self.session.record_corrected_command(query, corrected_command)

        # Setup mock for second execution
        self.mock_llm.get_improved_command.return_value = corrected_command

        # Second execution - should use corrected command
        success, output = self.session.execute_natural_language(query)

        # Verify that the LLM was queried for an improved command
        self.mock_llm.get_improved_command.assert_called_with(query, any, any)  # feedback data  # previous commands

        # Verify that the executor received the corrected command
        self.mock_executor.execute.assert_called_with(corrected_command)


class TestPluginIntegration(unittest.TestCase):
    """
    Test the integration of all standard plugins with the command pipeline.

    These tests verify that all standard plugins can generate commands
    that are properly executed.
    """

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        # Create real plugin registry and manager
        self.registry = PluginRegistry()
        self.plugin_manager = PluginManager()
        self.plugin_manager.registry = self.registry

        # Register all standard plugins
        self.file_plugin = FilePlugin()
        self.text_plugin = TextPlugin()
        self.system_plugin = SystemPlugin()
        self.network_plugin = NetworkPlugin()

        self.registry.register(self.file_plugin)
        self.registry.register(self.text_plugin)
        self.registry.register(self.system_plugin)
        self.registry.register(self.network_plugin)

        # Create mock executor that tracks commands
        self.mock_executor = MagicMock(spec=CommandExecutor)
        self.mock_executor.execute.return_value = (
            True,
            "Command executed successfully",
        )

        # Create mock LLM
        self.mock_llm = MagicMock(spec=LLMInterface)

        # Create parser with mock LLM
        self.parser = NaturalLanguageParser(llm=self.mock_llm)

        # Create session
        self.session = Session(
            parser=self.parser,
            plugin_manager=self.plugin_manager,
            executor=self.mock_executor,
            working_dir=str(self.test_dir),
        )

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_all_plugins_generate_commands(self):
        """Test that all plugins can generate commands."""
        test_cases = [
            # File plugin test cases
            ("ls", {"path": "/tmp"}, self.file_plugin),
            ("find", {"path": ".", "pattern": "*.txt"}, self.file_plugin),
            (
                "copy",
                {"source": "file1.txt", "destination": "file2.txt"},
                self.file_plugin,
            ),
            (
                "move",
                {"source": "file1.txt", "destination": "file2.txt"},
                self.file_plugin,
            ),
            ("delete", {"file": "file.txt"}, self.file_plugin),
            ("create", {"file": "newfile.txt"}, self.file_plugin),
            ("zip", {"files": "*.txt", "archive": "archive.zip"}, self.file_plugin),
            ("unzip", {"archive": "archive.zip"}, self.file_plugin),
            # Text plugin test cases
            ("grep", {"pattern": "error", "file": "log.txt"}, self.text_plugin),
            (
                "sed",
                {"pattern": "old", "replacement": "new", "file": "text.txt"},
                self.text_plugin,
            ),
            ("sort", {"file": "data.txt"}, self.text_plugin),
            ("wc", {"file": "text.txt"}, self.text_plugin),
            ("head", {"file": "log.txt", "lines": 10}, self.text_plugin),
            ("tail", {"file": "log.txt", "lines": 10}, self.text_plugin),
            # System plugin test cases
            ("ps", {}, self.system_plugin),
            ("top", {}, self.system_plugin),
            ("df", {}, self.system_plugin),
            ("du", {"path": "."}, self.system_plugin),
            ("free", {}, self.system_plugin),
            # Network plugin test cases
            ("ping", {"host": "localhost"}, self.network_plugin),
            ("wget", {"url": "https://example.com"}, self.network_plugin),
            ("curl", {"url": "https://example.com"}, self.network_plugin),
            ("nslookup", {"host": "example.com"}, self.network_plugin),
        ]

        for verb, args, expected_plugin in test_cases:
            # Test that the plugin can handle the verb
            self.assertTrue(
                expected_plugin.can_handle(verb),
                f"Plugin {expected_plugin.name} should handle verb '{verb}'",
            )

            # Test that the plugin manager finds the right plugin
            plugin = self.plugin_manager.get_plugin_for_verb(verb)
            self.assertEqual(
                plugin,
                expected_plugin,
                f"Plugin manager should find {expected_plugin.name} for verb '{verb}'",
            )

            # Test that the plugin can generate a command
            try:
                command = expected_plugin.generate_command(verb, args)
                self.assertIsInstance(
                    command,
                    str,
                    f"Plugin {expected_plugin.name} should generate a string command for verb '{verb}'",
                )
                self.assertGreater(
                    len(command),
                    0,
                    f"Plugin {expected_plugin.name} should generate a non-empty command for verb '{verb}'",
                )
            except Exception as e:
                self.fail(f"Plugin {expected_plugin.name} failed to generate command for verb '{verb}': {e}")

    def test_plugin_manager_command_generation(self):
        """Test that the plugin manager can generate commands for all verbs."""
        test_verbs = [
            "ls",
            "find",
            "copy",
            "move",
            "delete",
            "create",
            "zip",
            "unzip",  # File plugin
            "grep",
            "sed",
            "sort",
            "wc",
            "head",
            "tail",  # Text plugin
            "ps",
            "top",
            "df",
            "du",
            "free",  # System plugin
            "ping",
            "wget",
            "curl",
            "nslookup",  # Network plugin
        ]

        for verb in test_verbs:
            # Simple test arguments
            args = {
                "path": ".",
                "file": "test.txt",
                "host": "localhost",
                "url": "https://example.com",
            }

            # Test command generation
            success, command = self.plugin_manager.generate_command(verb, args)
            self.assertTrue(success, f"Plugin manager should generate command for verb '{verb}'")
            self.assertIsInstance(
                command,
                str,
                f"Plugin manager should return a string command for verb '{verb}'",
            )
            self.assertGreater(
                len(command),
                0,
                f"Plugin manager should return a non-empty command for verb '{verb}'",
            )


if __name__ == "__main__":
    unittest.main()
