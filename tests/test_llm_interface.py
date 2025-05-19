"""
Tests for the LLMInterface module.
"""

import io  # For capturing stderr
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from plainspeak.config import LLMConfig
from plainspeak.llm_interface import LLMInterface


class TestLLMInterface(unittest.TestCase):
    """Test suite for the LLMInterface class."""

    def setUp(self):
        """Set up test fixtures for each test."""
        # Initialize test fixtures
        self.patchers = []

        # Create config mock
        self.mock_llm_config = LLMConfig(
            model_path="config_default_model.gguf",
            model_type="config_default_type",
            gpu_layers=1,
            max_new_tokens=150,
            temperature=0.25,
            top_k=40,
            top_p=0.95,
            repetition_penalty=1.15,
            stop=["\n", "###"],
        )

        # Set up app config mock
        app_patcher = patch("plainspeak.llm_interface.app_config")
        self.mock_app_config_instance = app_patcher.start()
        self.mock_app_config_instance.llm = self.mock_llm_config
        self.patchers.append(app_patcher)

        # Set up model mock
        model_patcher = patch("ctransformers.AutoModelForCausalLM.from_pretrained")
        self.mock_from_pretrained = model_patcher.start()
        self.mock_model_instance = MagicMock()
        self.mock_from_pretrained.return_value = self.mock_model_instance
        self.patchers.append(model_patcher)

        # Create Path mock with required behavior
        self.mock_path = MagicMock(spec=Path)
        self.mock_path.exists.return_value = True
        self.mock_path.is_absolute.return_value = True
        self.mock_path.resolve.return_value = self.mock_path
        self.mock_path.__str__.return_value = self.mock_llm_config.model_path

        # Create CWD mock with path joining
        self.mock_cwd = MagicMock(spec=Path)
        self.mock_cwd.__str__.return_value = "/current/working/dir"

        def mock_truediv(_, other):
            if isinstance(other, (str, Path)):
                result = MagicMock(spec=Path)
                result.exists.return_value = True
                result.is_absolute.return_value = True
                result.resolve.return_value = result
                result.__str__.return_value = str(Path(self.mock_cwd.__str__.return_value) / str(other))
                return result
            return NotImplemented

        self.mock_cwd.__truediv__ = mock_truediv

        # Mock Path class constructor
        def mock_path_init(*args, **kwargs):
            if len(args) > 1:  # Path instance being created
                path_str = str(args[1])
                result = MagicMock(spec=Path)
                result.exists.return_value = True
                result.is_absolute.return_value = Path(path_str).is_absolute()
                result.resolve.return_value = result
                result.__str__.return_value = path_str
                return result
            return self.mock_path

        # Create and start Path-related patchers
        path_patches = [
            ("plainspeak.llm_interface.Path", mock_path_init),
            ("pathlib.Path", mock_path_init),
            ("pathlib.Path.cwd", MagicMock(return_value=self.mock_cwd)),
        ]

        # Start path patchers
        for target, new_value in path_patches:
            patcher = patch(target, new=new_value)
            patcher.start()
            self.patchers.append(patcher)

        # Store mock methods for test access
        self.mock_exists = self.mock_path.exists
        self.mock_is_absolute = self.mock_path.is_absolute
        self.mock_resolve = self.mock_path.resolve

    def tearDown(self):
        """Clean up test fixtures by stopping all patchers in reverse order."""
        for patcher in reversed(getattr(self, "patchers", [])):
            try:
                patcher.stop()
            except Exception as e:
                target = getattr(patcher, "_target", "unknown")
                print(
                    f"Warning: Failed to stop patcher {target}: {str(e)}",
                    file=sys.stderr,
                )

    def test_initialization_uses_app_config_defaults(self):
        """Test LLMInterface uses app_config when no args are passed."""
        llm_interface = LLMInterface()

        self.mock_from_pretrained.assert_called_once_with(
            self.mock_llm_config.model_path,
            model_type=self.mock_llm_config.model_type,
            gpu_layers=self.mock_llm_config.gpu_layers,
        )
        self.assertEqual(llm_interface.model_path, self.mock_llm_config.model_path)
        self.assertEqual(llm_interface.model_type, self.mock_llm_config.model_type)
        self.assertEqual(llm_interface.gpu_layers, self.mock_llm_config.gpu_layers)
        self.assertIsNotNone(llm_interface.model)

    def test_initialization_with_additional_kwargs(self):
        """Test LLMInterface initialization with additional ctransformers kwargs."""
        additional_kwargs = {
            "threads": 4,
            "batch_size": 8,
            "context_length": 2048,
            "seed": 42,
        }
        llm_interface = LLMInterface(**additional_kwargs)

        self.mock_from_pretrained.assert_called_once_with(
            self.mock_llm_config.model_path,
            model_type=self.mock_llm_config.model_type,
            gpu_layers=self.mock_llm_config.gpu_layers,
            **additional_kwargs,
        )
        self.assertEqual(llm_interface.ctransformers_config_kwargs, additional_kwargs)

    def test_initialization_overrides_app_config(self):
        """Test LLMInterface uses provided args over app_config."""
        custom_path = "override/model.gguf"
        custom_type = "override_type"
        custom_gpu_layers = 5

        # Setup path mocks
        self.mock_exists.return_value = True
        self.mock_is_absolute.return_value = True
        self.mock_resolve.return_value = Path(custom_path)

        # Create interface with custom settings
        llm_interface = LLMInterface(model_path=custom_path, model_type=custom_type, gpu_layers=custom_gpu_layers)

        # Verify correct path and settings were used
        self.mock_from_pretrained.assert_called_once_with(
            str(Path(custom_path)),  # Path should be converted to string
            model_type=custom_type,
            gpu_layers=custom_gpu_layers,
        )
        self.assertEqual(llm_interface.model_path, custom_path)
        self.assertEqual(llm_interface.model_type, custom_type)
        self.assertEqual(llm_interface.gpu_layers, custom_gpu_layers)

    def test_model_path_resolution_relative_to_cwd(self):
        """Test model path resolution relative to current working directory."""
        rel_path = "models/local.gguf"
        abs_path = "/current/working/dir/models/local.gguf"
        expected_path = Path(abs_path)

        # Configure mocks for this test
        self.mock_exists.return_value = True
        self.mock_is_absolute.return_value = False
        self.mock_resolve.return_value = expected_path

        llm_interface = LLMInterface(model_path=rel_path)

        self.assertEqual(llm_interface.model_path, str(expected_path))
        self.mock_from_pretrained.assert_called_once_with(
            str(expected_path),
            model_type=self.mock_llm_config.model_type,
            gpu_layers=self.mock_llm_config.gpu_layers,
        )

    def test_initialization_failure_file_not_found(self):
        """Test initialization failure if model file does not exist."""
        self.mock_exists.return_value = False

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            llm_interface = LLMInterface(model_path="nonexistent.gguf")
            self.assertIsNone(llm_interface.model)
            self.assertIn(
                "Error: Model file not found at 'nonexistent.gguf'",
                mock_stderr.getvalue(),
            )
            self.assertIn("Please ensure the model_path in your config", mock_stderr.getvalue())

    def test_initialization_failure_ctransformers_error(self):
        """Test initialization failure if ctransformers.from_pretrained errors."""
        error_message = "CUDA not available"
        self.mock_from_pretrained.side_effect = Exception(error_message)

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            llm_interface = LLMInterface()
            self.assertIsNone(llm_interface.model)
            stderr_output = mock_stderr.getvalue()
            self.assertIn(
                f"Error loading model from {self.mock_llm_config.model_path}: {error_message}",
                stderr_output,
            )
            self.assertIn("Please ensure the model path is correct", stderr_output)
            self.assertIn("For GPU usage, ensure CUDA/ROCm drivers", stderr_output)

    def test_generate_uses_app_config_defaults(self):
        """Test generate uses generation parameters from app_config by default."""
        llm_interface = LLMInterface()
        test_output = "Generated command: ls -la"
        self.mock_model_instance.generate.return_value = test_output

        result = llm_interface.generate("Test prompt")

        self.assertEqual(result, test_output)
        self.mock_model_instance.generate.assert_called_once_with(
            "Test prompt",
            max_new_tokens=self.mock_llm_config.max_new_tokens,
            temperature=self.mock_llm_config.temperature,
            top_k=self.mock_llm_config.top_k,
            top_p=self.mock_llm_config.top_p,
            repetition_penalty=self.mock_llm_config.repetition_penalty,
            stop=self.mock_llm_config.stop,
        )

    def test_generate_overrides_app_config_params(self):
        """Test generate uses provided args for generation over app_config."""
        llm_interface = LLMInterface()
        test_output = "Custom generated text"
        self.mock_model_instance.generate.return_value = test_output

        custom_params = {
            "max_new_tokens": 10,
            "temperature": 0.1,
            "top_k": 5,
            "top_p": 0.5,
            "repetition_penalty": 1.5,
            "stop": ["custom_stop"],
            "additional_param": "value",
        }
        result = llm_interface.generate("Test prompt", **custom_params)

        self.assertEqual(result, test_output)
        self.mock_model_instance.generate.assert_called_once_with("Test prompt", **custom_params)

    def test_generate_with_empty_stop_list(self):
        """Test generate with empty stop sequence list."""
        llm_interface = LLMInterface()
        test_output = "No stops output"
        self.mock_model_instance.generate.return_value = test_output

        result = llm_interface.generate("Test prompt", stop=[])

        call_args = self.mock_model_instance.generate.call_args[1]
        self.assertEqual(call_args["stop"], [])
        self.assertEqual(result, test_output)

    def test_generate_ctransformers_generation_error(self):
        """Test generate when model.generate() raises an error."""
        llm_interface = LLMInterface()
        error_message = "CUDA out of memory"
        self.mock_model_instance.generate.side_effect = Exception(error_message)

        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            result = llm_interface.generate("Test prompt")
            self.assertIsNone(result)
            self.assertIn(f"Error during text generation: {error_message}", mock_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
