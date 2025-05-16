"""
Tests for the LLMInterface module.
"""
import unittest
from unittest.mock import patch, MagicMock

# Ensure the plainspeak package is discoverable for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plainspeak.llm_interface import LLMInterface, DEFAULT_MODEL_PATH, DEFAULT_MODEL_TYPE

class TestLLMInterface(unittest.TestCase):
    """
    Test suite for the LLMInterface class.
    """

    @patch('ctransformers.AutoModelForCausalLM.from_pretrained')
    def test_initialization_success(self, mock_from_pretrained: MagicMock) -> None:
        """Test successful initialization of LLMInterface."""
        mock_model_instance = MagicMock()
        mock_from_pretrained.return_value = mock_model_instance

        llm_interface = LLMInterface(
            model_path="test/model.gguf",
            model_type="test_type",
            gpu_layers=10
        )

        mock_from_pretrained.assert_called_once_with(
            "test/model.gguf",
            model_type="test_type",
            gpu_layers=10
        )
        self.assertIsNotNone(llm_interface.model)
        self.assertEqual(llm_interface.model, mock_model_instance)
        self.assertEqual(llm_interface.model_path, "test/model.gguf")
        self.assertEqual(llm_interface.model_type, "test_type")
        self.assertEqual(llm_interface.gpu_layers, 10)

    @patch('ctransformers.AutoModelForCausalLM.from_pretrained')
    def test_initialization_failure(self, mock_from_pretrained: MagicMock) -> None:
        """Test initialization failure of LLMInterface."""
        mock_from_pretrained.side_effect = Exception("Model loading failed")

        with patch('builtins.print') as mock_print:
            llm_interface = LLMInterface() # Use default path which will fail
            mock_from_pretrained.assert_called_once_with(
                DEFAULT_MODEL_PATH, # Assuming default path is used
                model_type=DEFAULT_MODEL_TYPE,
                gpu_layers=0
            )
            self.assertIsNone(llm_interface.model)
            # Check if error messages were printed
            self.assertTrue(any("Error loading model" in call.args[0] for call in mock_print.call_args_list))

    @patch('ctransformers.AutoModelForCausalLM.from_pretrained')
    def test_generate_text_success(self, mock_from_pretrained: MagicMock) -> None:
        """Test successful text generation."""
        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = "Generated text"
        mock_from_pretrained.return_value = mock_model_instance

        llm_interface = LLMInterface()
        llm_interface.model = mock_model_instance # Ensure model is set

        prompt = "Test prompt"
        generated_text = llm_interface.generate(prompt, max_new_tokens=10)

        self.assertIsNotNone(generated_text)
        self.assertEqual(generated_text, "Generated text")
        mock_model_instance.generate.assert_called_once_with(
            prompt,
            max_new_tokens=10,
            temperature=0.7, # Default value
            top_k=50,        # Default value
            top_p=0.9,       # Default value
            repetition_penalty=1.1, # Default value
            stop=[]          # Default value
        )

    @patch('ctransformers.AutoModelForCausalLM.from_pretrained')
    def test_generate_text_model_not_loaded(self, mock_from_pretrained: MagicMock) -> None:
        """Test text generation when model is not loaded."""
        # Simulate model loading failure
        mock_from_pretrained.side_effect = Exception("Model loading failed")
        
        with patch('builtins.print') as mock_print:
            llm_interface = LLMInterface() # This will fail to load the model
            self.assertIsNone(llm_interface.model)
            
            generated_text = llm_interface.generate("Test prompt")
            self.assertIsNone(generated_text)
            self.assertTrue(any("Model not loaded. Cannot generate text." in call.args[0] for call in mock_print.call_args_list))


    @patch('ctransformers.AutoModelForCausalLM.from_pretrained')
    def test_generate_text_generation_failure(self, mock_from_pretrained: MagicMock) -> None:
        """Test text generation failure."""
        mock_model_instance = MagicMock()
        mock_model_instance.generate.side_effect = Exception("Generation error")
        mock_from_pretrained.return_value = mock_model_instance

        llm_interface = LLMInterface()
        llm_interface.model = mock_model_instance # Ensure model is set

        with patch('builtins.print') as mock_print:
            generated_text = llm_interface.generate("Test prompt")
            self.assertIsNone(generated_text)
            self.assertTrue(any("Error during text generation" in call.args[0] for call in mock_print.call_args_list))


if __name__ == '__main__':
    unittest.main()
