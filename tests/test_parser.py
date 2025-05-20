"""Tests for the natural language parser."""

import unittest
from unittest.mock import MagicMock

from plainspeak.core.parser import NaturalLanguageParser
from plainspeak.llm_interface import LLMInterface


class TestNaturalLanguageParser(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM
        self.mock_llm = MagicMock(spec=LLMInterface)
        self.mock_llm.generate_command.return_value = "ls -l"

        # Create parser with mock LLM
        self.parser = NaturalLanguageParser(self.mock_llm)

    def test_empty_input(self):
        """Test that empty input returns empty result."""
        result = self.parser.parse("")
        self.assertEqual(result, {"verb": None, "args": {}})

        result = self.parser.parse("   ")
        self.assertEqual(result, {"verb": None, "args": {}})

    def test_successful_parse(self):
        """Test successful command parsing."""
        # Test basic command
        self.mock_llm.generate_command.return_value = "ls /tmp"
        result = self.parser.parse("list files in temp")
        self.assertEqual(result, {"verb": "ls", "args": {"path": "/tmp"}})
        self.mock_llm.generate_command.assert_called_with("list files in temp")

        # Test command with options
        self.mock_llm.generate_command.return_value = "ls -l /home"
        result = self.parser.parse("show detailed list of home directory")
        self.assertEqual(result, {"verb": "ls", "args": {"path": "/home", "detail": True}})

    def test_llm_failure(self):
        """Test handling of LLM parsing failure."""
        self.mock_llm.generate_command.side_effect = Exception("LLM Error")
        result = self.parser.parse("list files")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "LLM Error")

    def test_llm_error_response(self):
        """Test handling of empty response from LLM."""
        # Test None response
        self.mock_llm.generate_command.return_value = None
        result = self.parser.parse("do something weird")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to generate command")

        # Test empty string response
        self.mock_llm.generate_command.return_value = ""
        result = self.parser.parse("do something")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to generate command")

    def test_with_plugin_manager(self):
        """Test parsing with plugin manager integration."""
        # Mock plugin manager
        mock_plugin_manager = MagicMock()
        mock_plugin = MagicMock()
        mock_plugin.name = "file_plugin"
        mock_plugin_manager.get_plugin_for_verb.return_value = mock_plugin

        # Create parser with mock LLM and plugin manager
        parser = NaturalLanguageParser(llm=self.mock_llm, plugin_manager=mock_plugin_manager)

        # Set up command return
        self.mock_llm.generate_command.return_value = "ls -l"

        # Test parsing
        result = parser.parse("list files")
        self.assertEqual(result["plugin"], "file_plugin")
        self.assertEqual(result["verb"], "ls")
        self.assertEqual(result["args"], {"path": ".", "detail": True})

        # Verify plugin lookup
        mock_plugin_manager.get_plugin_for_verb.assert_called_once_with("ls")

    def test_argument_parsing(self):
        """Test parsing of different argument patterns."""
        cases = [
            ("ls", {"path": "."}),
            ("ls -l", {"path": ".", "detail": True}),
            ("ls -r /tmp", {"path": "/tmp", "recursive": True}),
            ("ls --force", {"path": ".", "force": True}),
            ("ls -l -r /home", {"path": "/home", "detail": True, "recursive": True}),
            ("find --name test.txt", {"path": ".", "name": "test.txt"}),
        ]

        for cmd, expected_args in cases:
            self.mock_llm.generate_command.return_value = cmd
            result = self.parser.parse("dummy input")
            self.assertEqual(result["args"], expected_args)


if __name__ == "__main__":
    unittest.main()
