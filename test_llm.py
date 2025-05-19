"""Basic test runner for LLM interface tests."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from plainspeak.llm_interface import LLMInterface


class TestLLMInterface(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Create a test model path
        self.test_model_path = Path("/test/model.gguf")

        # Mock the model
        self.mock_model = MagicMock()
        self.mock_model.generate.return_value = "test output"

        # Set up patches
        self.patches = [
            patch("plainspeak.llm_interface.Path.exists", return_value=True),
            patch("plainspeak.llm_interface.Path.is_absolute", return_value=True),
            patch("plainspeak.llm_interface.Path.resolve", return_value=self.test_model_path),
            patch("plainspeak.llm_interface.Path.cwd", return_value=Path("/test")),
            patch("ctransformers.AutoModelForCausalLM.from_pretrained", return_value=self.mock_model),
        ]

        # Start all patches
        for p in self.patches:
            p.start()

        # Create LLM interface
        self.llm = LLMInterface(model_path=str(self.test_model_path), model_type="test_type")

    def tearDown(self):
        """Clean up patches."""
        for p in self.patches:
            p.stop()

    def test_generate(self):
        """Test the generate method."""
        expected_output = "Generated text"
        self.mock_model.generate.return_value = expected_output

        result = self.llm.generate("Test prompt")
        self.assertEqual(result, expected_output)

    def test_generate_with_params(self):
        """Test generate with custom parameters."""
        params = {
            "temperature": 0.5,
            "max_new_tokens": 100,
        }
        expected_output = "Custom generated text"
        self.mock_model.generate.return_value = expected_output

        result = self.llm.generate("Test prompt", **params)
        self.assertEqual(result, expected_output)

        # Verify the parameters were passed
        call_kwargs = self.mock_model.generate.call_args[1]
        for key, value in params.items():
            self.assertEqual(call_kwargs[key], value)


if __name__ == "__main__":
    unittest.main()
