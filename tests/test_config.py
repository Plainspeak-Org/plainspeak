"""
Tests for the configuration module.
"""
import unittest
from unittest.mock import patch, mock_open
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
            mock_print.assert_any_call(
                f"Warning: Could not load or parse config file {self.test_config_file}: "
                f"Unexpected character: '=' at line 1 col 30. Using default configuration."
            )
    
    def test_load_config_invalid_structure(self):
        """Test loading a TOML file with invalid structure (should use defaults for bad parts)."""
        self.test_config_dir.mkdir(exist_ok=True)
        # gpu_layers is an int, providing a string should cause Pydantic error
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
            # Pydantic validation error should lead to default config
            self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)
            self.assertEqual(config.llm.gpu_layers, 0) # Default
            mock_print.assert_any_call(
                f"Warning: Could not load or parse config file {self.test_config_file}: "
                f"1 validation error for AppConfig\nllm -> gpu_layers\n  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not_an_int', input_type=str]\n"
                f"    For further information visit https://errors.pydantic.dev/2.7/v/int_parsing. Using default configuration."
            )

    @patch('plainspeak.config.DEFAULT_CONFIG_FILE', Path("mock_default_config.toml"))
    @patch('plainspeak.config.DEFAULT_CONFIG_DIR', Path("mock_default_config_dir"))
    def test_ensure_default_config_exists(self, mock_dir_path, mock_file_path):
        """Test creation of default config file and directory if they don't exist."""
        mock_dir = mock_dir_path
        mock_file = mock_file_path

        if mock_file.exists(): mock_file.unlink()
        if mock_dir.exists(): mock_dir.rmdir()

        self.assertFalse(mock_dir.exists())
        self.assertFalse(mock_file.exists())

        with patch('builtins.print') as mock_print:
            ensure_default_config_exists()
        
        self.assertTrue(mock_dir.exists())
        self.assertTrue(mock_file.exists())
        
        # Verify content of created file
        config = load_config(mock_file)
        self.assertEqual(config.llm.model_path, DEFAULT_MODEL_FILE_PATH)

        # Clean up
        if mock_file.exists(): mock_file.unlink()
        if mock_dir.exists(): mock_dir.rmdir()

    @patch.dict(os.environ, {"PLAINSPEAK_PROJECT_ROOT": "/fake/project/root"})
    def test_resolve_model_path_project_root(self):
        """Test model path resolution relative to project root."""
        with patch('pathlib.Path.exists', return_value=True) as mock_exists:
            # Mock that /fake/project/root/models/model.gguf exists
            mock_exists.side_effect = lambda p: str(p) == "/fake/project/root/models/model.gguf"
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, "/fake/project/root/models/model.gguf")

    def test_resolve_model_path_home_dir(self):
        """Test model path resolution relative to home directory."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_absolute', return_value=False): # Ensure it's treated as relative
            
            # Mock that ~/models/model.gguf exists
            home_model_path = Path.home() / "models/model.gguf"
            mock_exists.side_effect = lambda p: p == home_model_path
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, str(home_model_path))

    def test_resolve_model_path_config_dir(self):
        """Test model path resolution relative to config directory."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_absolute', return_value=False):
            
            # Mock that ~/.config/plainspeak/models/model.gguf exists
            config_dir_model_path = DEFAULT_CONFIG_DIR / "models/model.gguf"
            mock_exists.side_effect = lambda p: p == config_dir_model_path
            
            config = LLMConfig(model_path="models/model.gguf")
            self.assertEqual(config.model_path, str(config_dir_model_path))

    def test_resolve_model_path_absolute(self):
        """Test model path resolution for an absolute path."""
        abs_path = "/absolute/path/to/model.gguf"
        with patch('pathlib.Path.exists', return_value=True) as mock_exists, \
             patch('pathlib.Path.is_absolute', return_value=True):
            
            config = LLMConfig(model_path=abs_path)
            self.assertEqual(config.model_path, abs_path)
            mock_exists.assert_called_once_with() # is_absolute is checked first

    def test_resolve_model_path_not_found_returns_original(self):
        """Test that if path is not found, original relative path is returned."""
        with patch('pathlib.Path.exists', return_value=False), \
             patch('pathlib.Path.is_absolute', return_value=False):
            
            config = LLMConfig(model_path="unresolvable/model.gguf")
            self.assertEqual(config.model_path, "unresolvable/model.gguf")

if __name__ == '__main__':
    unittest.main()
