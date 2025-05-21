"""
Configuration management for PlainSpeak.

This module handles loading and accessing application configuration,
such as LLM model paths, generation parameters, and other settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import toml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, field_validator

# Default configuration path
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "plainspeak"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"

# Default model path (can be overridden by config)
# This is the same as in llm_interface.py, but centralized here for clarity
DEFAULT_MODEL_FILE_PATH = "models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"


class LLMConfig(BaseModel):
    """LLM specific configuration."""

    provider: str = Field("local", description="LLM provider type (e.g., 'local', 'remote', 'openai').")
    model_path: Optional[str] = Field(DEFAULT_MODEL_FILE_PATH, description="Path to the GGUF model file.")
    model_type: str = Field("llama", description="Type of the model (e.g., 'llama', 'gptneox').")
    gpu_layers: int = Field(0, description="Number of model layers to offload to GPU. 0 for CPU only.")
    # Default generation parameters
    max_new_tokens: int = Field(256, description="Maximum new tokens for command generation.")
    max_tokens: int = Field(1024, description="Maximum tokens for remote LLM API calls.")
    temperature: float = Field(0.2, description="Sampling temperature for generation.")
    top_k: int = Field(50, description="Top-k sampling.")
    top_p: float = Field(0.9, description="Top-p (nucleus) sampling.")
    repetition_penalty: float = Field(1.1, description="Repetition penalty.")
    stop: Optional[list[str]] = Field(["\n"], description="Stop sequences for generation.")

    @field_validator("model_path", mode="before")  # type: ignore
    @classmethod
    def resolve_model_path(cls, v: Optional[str], values: Dict[str, Any]) -> str:  # type: ignore[misc]
        """
        If model_path is relative, try to resolve it relative to:
        1. Project root (if PLAINSPEAK_PROJECT_ROOT is set, e.g., during dev)
        2. User's home directory
        3. Default models directory within the config directory
        """
        if v is None:
            v = DEFAULT_MODEL_FILE_PATH

        path = Path(v)
        if path.is_absolute() and path.exists():
            return str(path)

        # Try relative to project root (useful for development)
        project_root_env = os.getenv("PLAINSPEAK_PROJECT_ROOT")
        if project_root_env:
            project_root_path = Path(project_root_env) / v
            if project_root_path.exists():
                return str(project_root_path)

        # Try relative to user's home directory
        home_path = Path.home() / v
        if home_path.exists():
            return str(home_path)

        # Try relative to default models dir in config dir
        config_models_path = DEFAULT_CONFIG_DIR / v
        if config_models_path.exists():
            return str(config_models_path)

        # If still not found and it's the default path, assume it's in `models/`
        # relative to where the app might be run from or a standard install location.
        # This path will be checked by LLMInterface at load time.
        return v


class AppConfig(BaseModel):
    """Main application configuration."""

    # Use a proper default factory to create a new LLMConfig instance
    llm: LLMConfig = Field(
        default_factory=lambda: LLMConfig(
            provider="local",
            model_path=DEFAULT_MODEL_FILE_PATH,
            model_type="llama",
            gpu_layers=0,
            max_new_tokens=256,
            max_tokens=1024,
            temperature=0.2,
            top_k=50,
            top_p=0.9,
            repetition_penalty=1.1,
            stop=["\n"],
        )
    )
    # Add other app-level configs here, e.g., log_level, etc.


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Loads configuration from a TOML file.
    If no path is provided, tries the default path.
    If the file doesn't exist or is invalid, returns default config.
    """
    path_to_load = config_path or DEFAULT_CONFIG_FILE

    if path_to_load.exists():
        try:
            config_data = toml.load(path_to_load)
            return AppConfig(**config_data)
        except (toml.TomlDecodeError, ValueError) as e:
            # Consider logging a warning here
            print(f"Warning: Could not load or parse config file {path_to_load}: {e}. Using default configuration.")
            return AppConfig()  # Return default config on error
    return AppConfig()  # Return default config if file not found


def ensure_default_config_exists():
    """
    Ensures the default config directory and a default config file exist.
    Creates them with default values if they don't.
    """
    if not DEFAULT_CONFIG_DIR.exists():
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not DEFAULT_CONFIG_FILE.exists():
        default_config = AppConfig()
        with open(DEFAULT_CONFIG_FILE, "w") as f:
            toml.dump(default_config.model_dump(), f)
        print(f"Created default configuration file at: {DEFAULT_CONFIG_FILE}")
        print(f"Please download the model '{DEFAULT_MODEL_FILE_PATH}' or update the model_path in the config.")


# Update the alias after AppConfig is defined
PlainSpeakConfig = AppConfig

# Global config instance, loaded on module import
# This can be reloaded if necessary by calling load_config() again.
# For a "century masterpiece", a more sophisticated DI or context-based approach might be used.
# For now, a global instance is simple and effective for this scale.
app_config: AppConfig = load_config()

if __name__ == "__main__":
    # Example of how to use the config module
    print(f"Loading configuration from: {DEFAULT_CONFIG_FILE}")

    # Ensure a default config is present for the example
    ensure_default_config_exists()

    # Reload to pick up any newly created default config
    current_config = load_config()

    print("\nCurrent LLM Configuration:")
    print(f"  Model Path: {current_config.llm.model_path}")
    print(f"  Model Type: {current_config.llm.model_type}")
    print(f"  GPU Layers: {current_config.llm.gpu_layers}")
    print(f"  Max New Tokens: {current_config.llm.max_new_tokens}")

    # Example of how to create a custom config file for testing
    # test_config_dir = Path(".") / "test_plainspeak_config"
    # test_config_file = test_config_dir / "test_config.toml"
    # if not test_config_dir.exists():
    #     test_config_dir.mkdir()

    # custom_settings = {
    #     "llm": {
    #         "model_path": "custom/path/to/model.gguf",
    #         "gpu_layers": 10,
    #         "temperature": 0.5
    #     }
    # }
    # with open(test_config_file, "w") as f:
    #     toml.dump(custom_settings, f)

    # print(f"\nLoading custom test configuration from: {test_config_file}")
    # custom_loaded_config = load_config(test_config_file)
    # print("\nCustom LLM Configuration:")
    # print(f"  Model Path: {custom_loaded_config.llm.model_path}")
    # print(f"  GPU Layers: {custom_loaded_config.llm.gpu_layers}")
    # print(f"  Temperature: {custom_loaded_config.llm.temperature}")

    # # Clean up test config
    # # test_config_file.unlink()
    # # test_config_dir.rmdir()
