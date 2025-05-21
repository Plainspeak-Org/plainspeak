"""
LLM Interface for PlainSpeak.

This module handles the loading and interaction with the
local Large Language Model (LLM) using the ctransformers library.
It uses the global application configuration for model paths and parameters.
"""

import sys
from pathlib import Path
from typing import Any, List, Optional

from ctransformers import AutoModelForCausalLM  # type: ignore[import-untyped]

from .config import app_config


class LLMInterface:
    """
    A class to interact with a GGUF model using ctransformers.
    Configuration is primarily sourced from app_config.llm.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        model_type: Optional[str] = None,
        gpu_layers: Optional[int] = None,
        **kwargs: Any,  # Additional ctransformers config options for AutoModelForCausalLM
    ):
        """
        Initializes the LLMInterface.

        Args:
            model_path (Optional[str]): Path to the GGUF model file. Overrides config if provided.
            model_type (Optional[str]): The type of the model. Overrides config if provided.
            gpu_layers (Optional[int]): Number of model layers to offload to GPU. Overrides config if provided.
            **kwargs: Additional configuration options to pass to AutoModelForCausalLM.
                      These will be merged with config-defined kwargs if any.
        """
        # Prioritize parameters over config, then fall back to config defaults
        # The model_path from app_config.llm.model_path is already resolved by the validator.
        self.model_path = model_path if model_path is not None else app_config.llm.model_path
        self.model_type = model_type if model_type is not None else app_config.llm.model_type
        self.gpu_layers = gpu_layers if gpu_layers is not None else app_config.llm.gpu_layers

        self.model: Optional[AutoModelForCausalLM] = None
        # For **kwargs, these are specific to AutoModelForCausalLM.from_pretrained
        self.ctransformers_config_kwargs = kwargs

        self._load_model()

    def _resolve_model_path(self) -> str:
        """
        Resolves the model path to an absolute path if possible.

        Resolution order:
        1. Use absolute path as-is if it exists
        2. If relative path, try relative to current working directory
        3. Fall back to original path if no resolution found

        Returns:
            str: The resolved path or original path
        """
        if not self.model_path:
            return ""

        # Convert to Path object for consistent handling
        path = Path(self.model_path)

        # If it's already absolute, use it as-is
        if path.is_absolute():
            return str(path)

        # If it's relative, try relative to current working directory
        cwd_path = Path.cwd() / path
        if cwd_path.exists():
            return str(cwd_path.resolve())

        # Return original path if no resolution found
        return self.model_path

    def _load_model(self) -> None:
        """
        Loads the GGUF model from the specified path.
        Handles path resolution and potential errors during model loading.
        """
        # Resolve the model path
        resolved_path = Path(self._resolve_model_path())
        if not resolved_path.exists():
            print(f"Error: Model file not found at '{self.model_path}'.", file=sys.stderr)
            print(
                "Please ensure the model_path in your config (or passed to LLMInterface) is correct.",
                file=sys.stderr,
            )
            self.model = None
            return

        try:
            # Convert to string for ctransformers
            str_path = str(resolved_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                str_path,
                model_type=self.model_type,
                gpu_layers=self.gpu_layers,
                **self.ctransformers_config_kwargs,
            )
            self.model_path = str_path  # Store resolved path
            print(f"Successfully loaded model from {self.model_path}", file=sys.stderr)
        except Exception as e:
            print(f"Error loading model from {self.model_path}: {e}", file=sys.stderr)
            print(
                "Please ensure the model path is correct and the GGUF file is valid.",
                file=sys.stderr,
            )
            print(
                "For GPU usage, ensure CUDA/ROCm drivers and ctransformers[cuda/rocm] are installed correctly.",
                file=sys.stderr,
            )
            self.model = None

    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        **kwargs: Any,  # Additional generation config options for model.generate()
    ) -> Optional[str]:
        """
        Generates text from the loaded LLM based on the given prompt.
        Generation parameters are taken from arguments if provided, otherwise from app_config.llm.

        Args:
            prompt (str): The input text prompt for the LLM.
            max_new_tokens (Optional[int]): Max new tokens. Overrides config.
            temperature (Optional[float]): Sampling temperature. Overrides config.
            top_k (Optional[int]): Top-k sampling. Overrides config.
            top_p (Optional[float]): Top-p sampling. Overrides config.
            repetition_penalty (Optional[float]): Repetition penalty. Overrides config.
            stop (Optional[List[str]]): Stop sequences. Overrides config.
            **kwargs: Additional generation parameters for the model's generate method.

        Returns:
            Optional[str]: The generated text, or None if model not loaded/generation fails.
        """
        if self.model is None:
            print("Model not loaded. Cannot generate text.", file=sys.stderr)
            return None

        # Use generation parameters from app_config.llm as defaults
        cfg_llm = app_config.llm

        final_max_new_tokens = max_new_tokens if max_new_tokens is not None else cfg_llm.max_new_tokens
        final_temperature = temperature if temperature is not None else cfg_llm.temperature
        final_top_k = top_k if top_k is not None else cfg_llm.top_k
        final_top_p = top_p if top_p is not None else cfg_llm.top_p
        final_repetition_penalty = repetition_penalty if repetition_penalty is not None else cfg_llm.repetition_penalty
        final_stop = stop if stop is not None else cfg_llm.stop

        try:
            full_generation_params = {
                "max_new_tokens": final_max_new_tokens,
                "temperature": final_temperature,
                "top_k": final_top_k,
                "top_p": final_top_p,
                "repetition_penalty": final_repetition_penalty,
                "stop": final_stop if final_stop else [],  # Ensure it's a list
                **kwargs,  # Pass through any other kwargs
            }

            result = self.model.generate(prompt, **full_generation_params)
            # Ensure we return a string or None
            return str(result) if result is not None else None
        except Exception as e:
            print(f"Error during text generation: {e}", file=sys.stderr)
            return None

    def generate_command(self, input_text: str) -> Optional[str]:
        """
        Generate a shell command from natural language input.

        This is a convenience wrapper around generate() that formats the prompt
        for command generation.

        Args:
            input_text: Natural language description of the desired command

        Returns:
            The generated command or None if generation failed
        """
        # Create a simple prompt for command generation
        prompt = f"""Generate a shell command that accomplishes the following task:
{input_text}

Return just the command with no explanation or markdown."""

        # Generate using default parameters
        return self.generate(prompt)


if __name__ == "__main__":
    print("Attempting to initialize LLMInterface using app_config...")
    llm = LLMInterface()

    if llm.model:
        print(
            f"\nLLMInterface initialized successfully with model: {llm.model_path}",
            file=sys.stderr,
        )
        test_prompt = (
            "Translate the following English text to a shell command: list all files in the current directory."
        )
        print(f"\nTesting generation with prompt: '{test_prompt}'", file=sys.stderr)

        generated_text = llm.generate(test_prompt)
        if generated_text:
            print("\nGenerated text:")
            print(generated_text)
        else:
            print("\nFailed to generate text.", file=sys.stderr)
    else:
        print(
            "\nFailed to initialize LLMInterface. Model could not be loaded.",
            file=sys.stderr,
        )
        print(
            "Please check your configuration or provide a valid model path.",
            file=sys.stderr,
        )
