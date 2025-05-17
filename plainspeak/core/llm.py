"""
LLM Interface for PlainSpeak.

This module provides an interface for interacting with language models
for natural language understanding and generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class LLMInterface(ABC):
    """
    Interface for language model interaction.
    
    This abstract class defines the interface for interacting with
    language models for natural language processing tasks.
    """
    
    @abstractmethod
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language into a structured format.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        pass
    
    def parse_natural_language_with_locale(self, text: str, locale: str) -> Dict[str, Any]:
        """
        Parse natural language with locale-specific context.
        
        Args:
            text: The natural language text to parse.
            locale: The locale code (e.g., "en_US").
            
        Returns:
            Dictionary with verb and arguments.
        """
        # Default implementation falls back to standard parsing
        return self.parse_natural_language(text)
    
    def get_improved_command(
        self, 
        query: str, 
        feedback_data: Dict[str, Any],
        previous_commands: List[str]
    ) -> str:
        """
        Generate an improved command based on feedback.
        
        Args:
            query: The original natural language query.
            feedback_data: Data about previous feedback.
            previous_commands: List of previously executed commands.
            
        Returns:
            Improved command string.
        """
        # Default implementation returns the last previous command or empty string
        if previous_commands:
            return previous_commands[-1]
        return ""
    
    def suggest_verbs(self, text: str) -> List[str]:
        """
        Suggest verbs based on partial input.
        
        Args:
            text: Partial natural language input.
            
        Returns:
            List of suggested verbs.
        """
        # Default implementation returns an empty list
        return []
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Args:
            text: Natural language text.
            
        Returns:
            Dictionary of entity types to values.
        """
        # Default implementation returns an empty dictionary
        return {}
    
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a command for the given verb and arguments.
        
        Args:
            verb: The verb to handle.
            args: Arguments for the verb.
            
        Returns:
            Generated command string.
        """
        # Default implementation returns a simple representation
        args_str = " ".join(f"{k}={v}" for k, v in args.items())
        return f"{verb} {args_str}"


class LocalLLM(LLMInterface):
    """
    Implementation of LLMInterface using a local language model.
    
    This class uses a local language model to parse natural language.
    """
    
    def __init__(
        self, 
        model_path: str,
        examples_path: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize the local LLM.
        
        Args:
            model_path: Path to the local model.
            examples_path: Optional path to examples file.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
        """
        self.model_path = model_path
        self.examples_path = examples_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Dictionary to store locale-specific prompts
        self.locale_prompts: Dict[str, str] = {}
        
        # Load the model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the local language model."""
        try:
            # Implementation depends on the specific model framework used
            # (e.g., ctransformers, llama-cpp-python, etc.)
            # Here we're just setting up a placeholder
            self.model = None
            self.model_loaded = False
            
            # In a real implementation, we would load the model here
            self.model_loaded = True
        except Exception as e:
            self.model_loaded = False
            raise RuntimeError(f"Failed to load model: {e}")
    
    def _get_prompt(self, text: str, locale: Optional[str] = None) -> str:
        """
        Get the prompt for the given text and locale.
        
        Args:
            text: The natural language text.
            locale: Optional locale code.
            
        Returns:
            Formatted prompt string.
        """
        # Use locale-specific prompt if available
        if locale and locale in self.locale_prompts:
            prompt_template = self.locale_prompts[locale]
        else:
            # Default English prompt
            prompt_template = """
            You are an assistant that translates natural language into structured commands.
            Parse the following natural language request into a verb and arguments.
            Output should be in the format {"verb": "command_verb", "args": {"arg1": "value1", ...}}
            
            Request: {text}
            
            Output:
            """
            
        return prompt_template.format(text=text)
    
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language using the local model.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not self.model_loaded:
            # Fall back to simple parsing if model isn't available
            return self._simple_parse(text)
            
        try:
            # Get the prompt
            prompt = self._get_prompt(text)
            
            # In a real implementation, we would generate text using the model
            # response = self.model.generate(prompt, temperature=self.temperature, max_tokens=self.max_tokens)
            
            # For now, use simple parsing as a placeholder
            return self._simple_parse(text)
            
        except Exception as e:
            # Fall back to simple parsing on error
            return self._simple_parse(text)
    
    def parse_natural_language_with_locale(self, text: str, locale: str) -> Dict[str, Any]:
        """
        Parse natural language with locale-specific context.
        
        Args:
            text: The natural language text to parse.
            locale: The locale code.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not self.model_loaded:
            return self._simple_parse(text)
            
        try:
            # Get the locale-specific prompt
            prompt = self._get_prompt(text, locale)
            
            # In a real implementation, we would generate text using the model
            # response = self.model.generate(prompt, temperature=self.temperature, max_tokens=self.max_tokens)
            
            # For now, use simple parsing as a placeholder
            return self._simple_parse(text)
            
        except Exception as e:
            return self._simple_parse(text)
    
    def _simple_parse(self, text: str) -> Dict[str, Any]:
        """
        Simple fallback parsing for when the model is unavailable.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not text:
            return {"verb": None, "args": {}}
            
        words = text.lower().split()
        
        if not words:
            return {"verb": None, "args": {}}
            
        # Use the first word as the verb
        verb = words[0]
        
        # Extract simple key=value pairs from the text
        args = {}
        for i, word in enumerate(words[1:], 1):
            if "=" in word:
                key, value = word.split("=", 1)
                args[key] = value
            elif i == len(words) - 1 and words[i-1] == "to" and verb in ["copy", "move"]:
                args["destination"] = word
            elif i == 1 and verb in ["list", "find", "show"]:
                args["path"] = word
                
        # If no args were extracted, use the rest as a single text argument
        if not args and len(words) > 1:
            args["text"] = " ".join(words[1:])
            
        return {"verb": verb, "args": args}
    
    def add_locale_prompt(self, locale: str, prompt_template: str) -> None:
        """
        Add a locale-specific prompt template.
        
        Args:
            locale: The locale code (e.g., "fr_FR").
            prompt_template: The prompt template with {text} placeholder.
        """
        self.locale_prompts[locale] = prompt_template
    
    def get_improved_command(
        self, 
        query: str, 
        feedback_data: Dict[str, Any],
        previous_commands: List[str]
    ) -> str:
        """
        Generate an improved command based on feedback.
        
        Args:
            query: The original natural language query.
            feedback_data: Data about previous feedback.
            previous_commands: List of previously executed commands.
            
        Returns:
            Improved command string.
        """
        # In a real implementation, we would use the model to generate an improved command
        if "corrected_command" in feedback_data:
            return feedback_data["corrected_command"]
        
        # Fall back to the last previous command or empty string
        if previous_commands:
            return previous_commands[-1]
        
        return ""


class RemoteLLM(LLMInterface):
    """
    Implementation of LLMInterface using a remote API.
    
    This class calls a remote API for natural language processing.
    """
    
    def __init__(
        self, 
        api_endpoint: str,
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ):
        """
        Initialize the remote LLM.
        
        Args:
            api_endpoint: URL of the API endpoint.
            api_key: Optional API key.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language using the remote API.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not text:
            return {"verb": None, "args": {}}
            
        try:
            # In a real implementation, we would call the API here
            # For now, use a simple placeholder implementation
            return self._simple_parse(text)
        except Exception as e:
            # Fall back to simple parsing on error
            return self._simple_parse(text)
    
    def parse_natural_language_with_locale(self, text: str, locale: str) -> Dict[str, Any]:
        """
        Parse natural language with locale-specific context.
        
        Args:
            text: The natural language text to parse.
            locale: The locale code.
            
        Returns:
            Dictionary with verb and arguments.
        """
        if not text:
            return {"verb": None, "args": {}}
            
        try:
            # In a real implementation, we would call the API with locale info
            # For now, use a simple placeholder implementation
            return self._simple_parse(text)
        except Exception as e:
            return self._simple_parse(text)
    
    def _simple_parse(self, text: str) -> Dict[str, Any]:
        """
        Simple fallback parsing for when the API is unavailable.
        
        Args:
            text: The natural language text to parse.
            
        Returns:
            Dictionary with verb and arguments.
        """
        # Same implementation as in LocalLLM
        if not text:
            return {"verb": None, "args": {}}
            
        words = text.lower().split()
        
        if not words:
            return {"verb": None, "args": {}}
            
        # Use the first word as the verb
        verb = words[0]
        
        # Extract simple key=value pairs from the text
        args = {}
        for i, word in enumerate(words[1:], 1):
            if "=" in word:
                key, value = word.split("=", 1)
                args[key] = value
            elif i == len(words) - 1 and words[i-1] == "to" and verb in ["copy", "move"]:
                args["destination"] = word
            elif i == 1 and verb in ["list", "find", "show"]:
                args["path"] = word
                
        # If no args were extracted, use the rest as a single text argument
        if not args and len(words) > 1:
            args["text"] = " ".join(words[1:])
            
        return {"verb": verb, "args": args} 