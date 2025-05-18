"""
Tests for the command parser module.
"""

import unittest
from unittest.mock import Mock, patch

from plainspeak.llm_interface import LLMInterface
from plainspeak.parser import CommandParser


class TestCommandParser(unittest.TestCase):
    """Test suite for the CommandParser class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock LLM interface
        self.mock_llm = Mock(spec=LLMInterface)
        self.parser = CommandParser(llm=self.mock_llm)

    def test_empty_input(self):
        """Test that empty input is rejected."""
        success, result = self.parser.parse_to_command("")
        self.assertFalse(success)
        self.assertEqual(result, "ERROR: Empty input")

        success, result = self.parser.parse_to_command("   ")
        self.assertFalse(success)
        self.assertEqual(result, "ERROR: Empty input")

    def test_successful_parse(self):
        """Test successful command generation."""
        self.mock_llm.generate.return_value = "ls -l"
        success, result = self.parser.parse_to_command("list files in detail")
        self.assertTrue(success)
        self.assertEqual(result, "ls -l")

    def test_llm_failure(self):
        """Test handling of LLM generation failure."""
        self.mock_llm.generate.return_value = None
        success, result = self.parser.parse_to_command("list files")
        self.assertFalse(success)
        self.assertEqual(result, "ERROR: Failed to generate command")

    def test_llm_error_response(self):
        """Test handling of LLM error responses."""
        self.mock_llm.generate.return_value = "ERROR: Unclear or ambiguous request"
        success, result = self.parser.parse_to_command("do something weird")
        self.assertFalse(success)
        self.assertEqual(result, "ERROR: Unclear or ambiguous request")

    def test_unsafe_commands(self):
        """Test detection of unsafe command patterns."""
        unsafe_commands = {
            "rm -rf /": "rm -rf",
            "sudo apt-get update": "sudo",
            "echo 'hello' > file.txt": ">",
            "ls -l | grep test": "|",
            "cd /tmp && rm *": "&&",
            "test || echo failed": "||",
            "echo $(whoami)": "$(",
            "echo `whoami`": "`",
            "command1; command2": ";",
            "mkfs.ext4 /dev/sda1": "mkfs",
        }

        for cmd, pattern in unsafe_commands.items():
            self.mock_llm.generate.return_value = cmd
            success, result = self.parser.parse_to_command("some input")
            self.assertFalse(success, f"Should reject unsafe command: {cmd}")
            self.assertIn(pattern, result)
            self.assertIn("ERROR:", result)

    @patch("platform.system")
    @patch("os.environ.get")
    def test_system_context_generation(self, mock_environ_get, mock_platform_system):
        """Test system context generation with different environments."""
        test_cases = [
            # (platform, shell, expected_os, expected_shell)
            ("Darwin", "/bin/zsh", "macOS", "Zsh"),
            ("Linux", "/bin/bash", "linux", "Bash"),
            ("Linux", "/usr/bin/fish", "linux", "Fish"),
            ("Windows", "cmd.exe", "windows", "standard shell"),
        ]

        for platform_name, shell_path, exp_os, exp_shell in test_cases:
            mock_platform_system.return_value = platform_name
            mock_environ_get.return_value = shell_path

            context = self.parser._get_system_context()
            self.assertIn(exp_os.lower(), context.lower())
            self.assertIn(exp_shell, context)

    def test_custom_generation_params(self):
        """Test that custom generation parameters are used."""
        custom_params = {
            "temperature": 0.1,
            "max_new_tokens": 50,
            "top_p": 0.95,
            "custom_param": "test",
        }

        parser = CommandParser(llm=self.mock_llm, generation_params=custom_params)

        parser.parse_to_command("list files")

        # Check that the LLM's generate method was called with our custom params
        self.mock_llm.generate.assert_called_once()
        call_args = self.mock_llm.generate.call_args[1]
        for key, value in custom_params.items():
            self.assertEqual(call_args[key], value)
