"""
Tests for the configuration module.
"""

import unittest
from pathlib import Path
from unittest.mock import patch

from plainspeak.config import LLMConfig


class TestConfig(unittest.TestCase):
    """Test suite for configuration loading and management."""

    def test_resolve_model_path_absolute(self):
        """Test model path resolution for an absolute path."""
        abs_path_str = "/absolute/path/to/model.gguf"
        abs_path = Path(abs_path_str)

        # Mock is_absolute to return True for this specific path, and exists to also be True
        def mock_is_absolute_side_effect(path_instance):
            return path_instance == abs_path

        def mock_exists_side_effect(path_instance):
            return path_instance == abs_path

        with (
            patch(
                "pathlib.Path.is_absolute",
                side_effect=mock_is_absolute_side_effect,
                autospec=True,
            ),
            patch(
                "pathlib.Path.exists",
                side_effect=mock_exists_side_effect,
                autospec=True,
            ),
        ):
            config = LLMConfig(model_path=abs_path_str)
            self.assertEqual(config.model_path, abs_path_str)
