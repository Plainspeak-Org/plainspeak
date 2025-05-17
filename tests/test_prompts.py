"""
Tests for the prompts module.
"""

import unittest
from plainspeak.prompts import get_shell_command_prompt


class TestPrompts(unittest.TestCase):
    """Test suite for prompt templates."""

    def test_shell_command_prompt_basic(self):
        """Test basic shell command prompt formatting."""
        input_text = "list all files"
        expected_substring = 'Given this request in plain English:\n"list all files"'
        result = get_shell_command_prompt(input_text)
        self.assertIn(expected_substring, result)
        self.assertIn("Additional context: Unix-like environment", result)

    def test_shell_command_prompt_custom_context(self):
        """Test shell command prompt with custom context."""
        input_text = "list all files"
        context = "Windows PowerShell environment"
        result = get_shell_command_prompt(input_text, context)
        self.assertIn(context, result)

    def test_shell_command_prompt_guidelines(self):
        """Test that the prompt includes the important guidelines."""
        result = get_shell_command_prompt("any command")
        self.assertIn("Output ONLY the command", result)
        self.assertIn("Use standard Unix/Linux shell syntax", result)
        self.assertIn("Use common utilities", result)
        self.assertIn("ERROR: ", result)  # Should mention error format

    def test_shell_command_prompt_escaping(self):
        """Test that the prompt handles inputs with quotes properly."""
        input_with_quotes = 'find files containing "error" in them'
        result = get_shell_command_prompt(input_with_quotes)
        self.assertIn(input_with_quotes, result)
        # The template should maintain proper quote balance
        # Input text is wrapped in quotes, followed by newlines and the Command: label
        self.assertIn('"\n\nGenerate a single shell command', result)
