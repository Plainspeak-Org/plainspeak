"""
Test the command translation for system-specific commands.
"""

import unittest
from unittest.mock import MagicMock

from plainspeak.core.llm import LLMInterface


class TestImprovedPrompting(unittest.TestCase):
    """Test the improved prompting for system commands."""

    def test_generate_command_includes_guidance(self):
        """Test that the generate_command method includes the guidance in the prompt."""
        mock_llm = LLMInterface()
        mock_llm.generate = MagicMock(return_value="systemctl list-unit-files --type=service --state=enabled")
        mock_llm._get_system_prompt = MagicMock(return_value="System prompt")

        mock_llm.generate_command("List all services that start at boot")

        # Check that the mock was called with a prompt that includes guidance
        prompt = mock_llm.generate.call_args[0][0]
        self.assertIn("IMPORTANT GUIDANCE:", prompt)
        self.assertIn("Never return partial, placeholder, or generic commands", prompt)

    def test_parse_intent_uses_enhanced_prompt(self):
        """Test that parse_intent uses the enhanced prompt."""
        mock_llm = LLMInterface()
        mock_llm.generate = MagicMock(return_value="systemctl list-unit-files --type=service --state=enabled")
        mock_llm._get_system_prompt = MagicMock(return_value="System prompt")

        mock_llm.parse_intent("List all services that start at boot")

        # Check that the mock was called with an enhanced prompt
        prompt = mock_llm.generate.call_args[0][0]
        self.assertIn("IMPORTANT GUIDANCE:", prompt)
        self.assertIn("never return", prompt.lower())

    def test_parse_natural_language_with_locale_uses_enhanced_prompt(self):
        """Test that parse_natural_language_with_locale uses the enhanced prompt."""
        mock_llm = LLMInterface()
        mock_llm.generate = MagicMock(return_value="systemctl list-unit-files --type=service --state=enabled")
        mock_llm._get_system_prompt = MagicMock(return_value="System prompt")
        mock_llm._parse_llm_response = MagicMock(return_value={"verb": "systemctl", "args": {}})

        mock_llm.parse_natural_language_with_locale("List all services that start at boot", "en_US")

        # Check that the mock was called with an enhanced prompt
        prompt = mock_llm.generate.call_args[0][0]
        self.assertIn("IMPORTANT GUIDANCE:", prompt)
        self.assertIn("Consider the locale", prompt)


if __name__ == "__main__":
    unittest.main()
