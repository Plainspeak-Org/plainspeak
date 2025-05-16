"""
LLM Interface for PlainSpeak.

This module handles the loading and interaction with the
local Large Language Model (LLM) using the ctransformers library.
"""
from ctransformers import AutoModelForCausalLM, AutoConfig, Config
from typing import Optional, List, Dict, Any

# Default model path - points to the recommended small development model.
# Users need to download the model file first:
# https://huggingface.co/TheBloke/MiniCPM-2B-SFT-GGUF/resolve/main/minicpm-2b-sft.Q2_K.gguf
DEFAULT_MODEL_PATH = "models/minicpm-2b-sft.Q2_K.gguf"
DEFAULT_MODEL_TYPE = "llama"  # MiniCPM is based on Llama architecture

class LLMInterface:
    """
    A class to interact with a GGUF model using ctransformers.
    """

    def __init__(
        self,
        model_path: str = DEFAULT_MODEL_PATH,
        model_type: str = DEFAULT_MODEL_TYPE,
        gpu_layers: int = 0, # Number of layers to offload to GPU. 0 for CPU only.
        **kwargs: Any # Additional ctransformers config options
    ):
        """
        Initializes the LLMInterface.

        Args:
            model_path (str): Path to the GGUF model file.
            model_type (str): The type of the model (e.g., 'llama', 'gptneox').
                              This helps ctransformers load the model correctly.
            gpu_layers (int): Number of model layers to offload to GPU.
                              Set to 0 for CPU-only inference.
            **kwargs: Additional configuration options to pass to AutoModelForCausalLM.
                      See ctransformers documentation for available options.
        """
        self.model_path = model_path
        self.model_type = model_type
        self.gpu_layers = gpu_layers
        self.model: Optional[AutoModelForCausalLM] = None
        self.config_kwargs = kwargs

        self._load_model()

    def _load_model(self) -> None:
        """
        Loads the GGUF model from the specified path.
        Handles potential errors during model loading.
        """
        try:
            # More detailed config if needed
            # config = AutoConfig(Config(gpu_layers=self.gpu_layers, **self.config_kwargs))
            # self.model = AutoModelForCausalLM.from_pretrained(
            #     self.model_path,
            #     model_type=self.model_type,
            #     config=config
            # )
            # Simpler loading for now, can be expanded
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                model_type=self.model_type,
                gpu_layers=self.gpu_layers,
                **self.config_kwargs
            )
            print(f"Successfully loaded model from {self.model_path}")
        except Exception as e:
            # Consider more specific exception handling if ctransformers provides it
            print(f"Error loading model from {self.model_path}: {e}")
            print("Please ensure the model path is correct and the GGUF file is valid.")
            print("For GPU usage, ensure CUDA/ROCm drivers and ctransformers[cuda/rocm] are installed correctly.")
            self.model = None # Ensure model is None if loading fails

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        stop: Optional[List[str]] = None,
        **kwargs: Any # Additional generation config options
    ) -> Optional[str]:
        """
        Generates text from the loaded LLM based on the given prompt.

        Args:
            prompt (str): The input text prompt for the LLM.
            max_new_tokens (int): Maximum number of new tokens to generate.
            temperature (float): Controls randomness. Lower is more deterministic.
            top_k (int): Consider only top_k most likely tokens.
            top_p (float): Consider tokens with cumulative probability >= top_p.
            repetition_penalty (float): Penalizes repeated tokens.
            stop (Optional[List[str]]): A list of strings to stop generation at.
            **kwargs: Additional generation parameters for the model's generate method.

        Returns:
            Optional[str]: The generated text, or None if the model is not loaded
                           or generation fails.
        """
        if self.model is None:
            print("Model not loaded. Cannot generate text.")
            return None

        try:
            # Ensure prompt is correctly formatted if model expects specific templating
            # For now, passing prompt directly
            full_generation_params = {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "stop": stop if stop else [],
                **kwargs
            }
            
            # Some models might stream output. For now, getting the full result.
            # result = self.model(prompt, **full_generation_params)
            # For streaming:
            # tokens = []
            # for token_str in self.model(prompt, stream=True, **full_generation_params):
            #     tokens.append(token_str)
            # result = "".join(tokens)

            # Direct generation call
            result = self.model.generate(prompt, **full_generation_params)

            return result
        except Exception as e:
            print(f"Error during text generation: {e}")
            return None

if __name__ == "__main__":
    # This is a basic example of how to use the LLMInterface.
    # It requires a GGUF model file at the DEFAULT_MODEL_PATH.
    
    print("Attempting to initialize LLMInterface...")
    # Replace with actual model path and type if DEFAULT_MODEL_PATH is a placeholder
    # For example, if you have 'TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q4_K_M.gguf'
    # llm = LLMInterface(model_path="path/to/your/mistral-7b-instruct-v0.1.Q4_K_M.gguf", model_type="mistral")
    
    # Using placeholder path - this will likely fail unless model exists there
    llm = LLMInterface(model_path=DEFAULT_MODEL_PATH, model_type=DEFAULT_MODEL_TYPE)

    if llm.model:
        print("\nLLMInterface initialized successfully.")
        test_prompt = "Translate the following English text to a shell command: list all files in the current directory."
        print(f"\nTesting generation with prompt: '{test_prompt}'")
        
        generated_text = llm.generate(test_prompt, max_new_tokens=50)
        
        if generated_text:
            print("\nGenerated text:")
            print(generated_text)
        else:
            print("\nFailed to generate text.")
    else:
        print("\nFailed to initialize LLMInterface. Model could not be loaded.")
        print(f"Please check that a valid GGUF model exists at '{DEFAULT_MODEL_PATH}' or provide a correct path.")

# Notes on the LLMInterface:
# This code provides a basic structure for loading and interacting with a GGUF model.
# It includes:
# - Initialization with model path, type, and GPU layers.
# - A `_load_model` method with basic error handling.
# - A `generate` method to produce text, with common generation parameters.
# - A simple `if __name__ == "__main__":` block for testing (which will likely fail until `DEFAULT_MODEL_PATH` is set to a valid model).

# Next steps would involve:
# 1.  Selecting and downloading a suitable GGUF model (e.g., a MiniCPM variant or similar).
# 2.  Updating `DEFAULT_MODEL_PATH` or providing a configuration mechanism for it.
# 3.  Creating tests for this interface (mocking the `ctransformers` calls or using a very small dummy model if possible).
# 4.  Integrating this `LLMInterface` into the main PlainSpeak application flow (parser component).
