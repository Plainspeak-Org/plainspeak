"""
Tests for the configuration module.
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import toml
from pathlib import Path
from pydantic import ValidationError

from plainspeak.config import (
    AppConfig,
    LLMConfig,
    load_config,
    ensure_default_config_exists,
    DEFAULT_CONFIG_FILE,
    DEFAULT_CONFIG_DIR,
    DEFAULT_MODEL_FILE_PATH
)

class TestConfig(unittest.TestCase):
    """Test suite for configuration loading and management."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config_dir = Path(".") / "test_plainspeak_temp_config"
        self.test_config_file = self.test_config_dir / "test_config.toml"
        
        # Ensure clean state for each test
        if self.test_config_file.exists():
            self.test_config_file.unlink()
        if self.test_config_dir.exists():
            self.test_config_dir.rmdir() # Should be empty

    def tearDown(self):
        """Clean up after tests."""
        if self.test_config_file.exists():
            self.test_config_file.unlink()
        if self.test_config_dir.exists():
            self.test_config_dir.rmdir()

    def test_default_llm_config(self):
        """Test default LLMConfig values."""
        config = LLMConfig()
        self.assertEqual(config.model_path, DEFAULT_MODEL_FILE_PATH)
        self.assertEqual(config.model_type, "llama")
        self.assertEqual(config.gpu_layers, 0)
        self.assertEqual(config.max_new_tokens, 100)
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.stop, ["\n"])

    def test_default_app_config(self):
        """Test default AppConfig."""
        config = AppConfig()
        self.assertIsInstance(config.llm, LLMConfig)

    def test_load_config_non_existent_file(self):
        """Test loading config when file does not exist (should return defaults)."""
        config = load_config(Path("non_existent_config.toml"))
        self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)

    def test_load_config_valid_file(self):
        """Test loading a valid TOML configuration file."""
        self.test_config_dir.mkdir(exist_ok=True)
        custom_settings = {
            "llm": {
                "model_path": "custom/model.gguf",
                "gpu_layers": 10,
                "temperature": 0.7
            }
        }
        with open(self.test_config_file, "w") as f:
            toml.dump(custom_settings, f)

        config = load_config(self.test_config_file)
        self.assertEqual(config.llm.model_path, "custom/model.gguf")
        self.assertEqual(config.llm.gpu_layers, 10)
        self.assertEqual(config.llm.temperature, 0.7)
        # Unset values should retain defaults
        self.assertEqual(config.llm.model_type, "llama") 

    def test_load_config_invalid_toml(self):
        """Test loading an invalid TOML file (should return defaults and print warning)."""
        self.test_config_dir.mkdir(exist_ok=True)
        with open(self.test_config_file, "w") as f:
            f.write("this is not valid toml content = ")

        with patch('builtins.print') as mock_print:
            config = load_config(self.test_config_file)
            self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)
            # Updated TOML error message based on actual test output
            printed_text = "".join(call_args[0][0] for call_args in mock_print.call_args_list)
            self.assertIn(f"Warning: Could not load or parse config file {self.test_config_file}", printed_text)
            self.assertIn("Found invalid character in key name: 'i'", printed_text) # Key part of the TOML error
            self.assertIn("Using default configuration.", printed_text)
    
    def test_load_config_invalid_structure(self):
        """Test loading a TOML file with invalid structure (should use defaults for bad parts)."""
        self.test_config_dir.mkdir(exist_ok=True)
        custom_settings = {
            "llm": {
                "model_path": "another/model.gguf",
                "gpu_layers": "not_an_int" 
            }
        }
        with open(self.test_config_file, "w") as f:
            toml.dump(custom_settings, f)

        with patch('builtins.print') as mock_print:
            config = load_config(self.test_config_file)
            self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)
            self.assertEqual(config.llm.gpu_layers, 0) # Default
            
            printed_text = "".join(call_args[0][0] for call_args in mock_print.call_args_list)
            self.assertIn(f"Warning: Could not load or parse config file {self.test_config_file}", printed_text)
            self.assertIn("1 validation error for AppConfig", printed_text)
            self.assertIn("llm.gpu_layers", printed_text)  # Updated for Pydantic V2 format
            self.assertIn("Input should be a valid integer", printed_text)
            self.assertIn("input_value='not_an_int'", printed_text)
            self.assertIn("https://errors.pydantic.dev/2.11/v/int_parsing", printed_text) 
            self.assertIn("Using default configuration.", printed_text)

    def test_ensure_default_config_exists(self):
        """Test creation of default config file and directory."""
        # Create a test directory for this specific test
        test_config_dir = Path("./test_config_dir")
        test_config_file = test_config_dir / "test_config.toml"

        try:
            # Patch both the directory and file paths
            with patch('plainspeak.config.DEFAULT_CONFIG_DIR', test_config_dir), \
                 patch('plainspeak.config.DEFAULT_CONFIG_FILE', test_config_file), \
                 patch('builtins.print'):  # Suppress output during test
                
                # Ensure we start clean
                if test_config_file.exists():
                    test_config_file.unlink()
                if test_config_dir.exists():
                    test_config_dir.rmdir()

                self.assertFalse(test_config_dir.exists())
                self.assertFalse(test_config_file.exists())

                # Run the function
                ensure_default_config_exists()

                # Verify the results
                self.assertTrue(test_config_dir.exists())
                self.assertTrue(test_config_file.exists())

                # Check the content
                config = load_config(test_config_file)
                self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)

        finally:
            # Clean up
            if test_config_file.exists():
                test_config_file.unlink()
            if test_config_dir.exists():
                test_config_dir.rmdir()

    @patch.dict(os.environ, {"PLAINSPEAK_PROJECT_ROOT": "/fake/project/root"})
    def test_resolve_model_path_project_root(self):
        """Test model path resolution relative to project root."""
        expected_path = Path("/fake/project/root/models/model.gguf")
        with patch('pathlib.Path.exists', autospec=True) as mock_exists:
            mock_exists.side_effect = lambda path_instance: path_instance == expected_path
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, str(expected_path))

    def test_resolve_model_path_home_dir(self):
        """Test model path resolution relative to home directory."""
        expected_path = Path.home() / "models/model.gguf"
        with patch('pathlib.Path.exists', autospec=True) as mock_exists, \
             patch('pathlib.Path.is_absolute', return_value=False):
            
            mock_exists.side_effect = lambda path_instance: path_instance == expected_path
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, str(expected_path))

    def test_resolve_model_path_config_dir(self):
        """Test model path resolution relative to config directory."""
        expected_path = DEFAULT_CONFIG_DIR / "models/model.gguf"
        with patch('pathlib.Path.exists', autospec=True) as mock_exists, \
             patch('pathlib.Path.is_absolute', return_value=False):
            
            mock_exists.side_effect = lambda path_instance: path_instance == expected_path
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, str(expected_path))

    def test_resolve_model_path_absolute(self):
        """Test model path resolution for an absolute path."""
        abs_path_str = "/absolute/path/to/model.gguf"
        abs_path = Path(abs_path_str)
        
        # Mock is_absolute to return True for this specific path, and exists to also be True
        def mock_is_absolute_side_effect(path_instance):
            return path_instance == abs_path

        def mock_exists_side_effect(path_instance):
            return path_instance == abs_path

        with patch('pathlib.Path.is_absolute', side_effect=mock_is_absolute_side_effect, autospec=True), \
             patch('pathlib.Path.exists', side_effect=mock_exists_side_effect, autospec=True) as mock_exists_method:
            
            config = LLMConfig(model_path=abs_path_str)
            self.assertEqual(config.model_path, abs_path_str)
            # Check that Path(abs_path_str).is_absolute() was called, then Path(abs_path_str).exists()
            # The validator calls is_absolute first. If true, it then calls exists.
            # So, exists should be called on the original absolute path.
            # mock_exists_method.assert_any_call(abs_path) # This checks if the method was called with abs_path as self

    def test_resolve_model_path_not_found_returns_original(self):
        """Test that if path is not found, original relative path is returned."""
        with patch('pathlib.Path.exists', return_value=False, autospec=True), \
             patch('pathlib.Path.is_absolute', return_value=False, autospec=True):
            
            config = LLMConfig(model_path="unresolvable/model.gguf")
            self.assertEqual(config.model_path, "unresolvable/model.gguf")

if __name__ == '__main__':
    unittest.main()
