"""
LLM Interface for PlainSpeak.

This module provides an interface for interacting with language models
for natural language understanding and generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
import os
import json
import requests
import uuid
import logging
import ssl
import certifi
from functools import lru_cache


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
        max_tokens: int = 2048,
        timeout: int = 30,
        verify_ssl: bool = True,
        retry_count: int = 3,
        ssl_cert_path: Optional[str] = None
    ):
        """
        Initialize the remote LLM.
        
        Args:
            api_endpoint: URL of the API endpoint.
            api_key: Optional API key.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            timeout: Request timeout in seconds.
            verify_ssl: Whether to verify SSL certificates.
            retry_count: Number of retries for failed requests.
            ssl_cert_path: Path to custom SSL certificate.
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_count = retry_count
        
        # Configure SSL verification
        self.verify_ssl = certifi.where() if verify_ssl else False
        if ssl_cert_path and os.path.exists(ssl_cert_path):
            self.verify_ssl = ssl_cert_path
            
        # Setup logging
        self.logger = logging.getLogger("RemoteLLM")
        
        # Track API calls for rate limiting
        self.request_count = 0
        self.request_ids = {}
        
    def _make_api_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a secure API request with proper error handling and retry logic.
        
        Args:
            endpoint: API endpoint path to append to base URL.
            payload: Request payload.
            
        Returns:
            Response data as dictionary.
            
        Raises:
            RuntimeError: If API request fails after all retries.
        """
        # Generate a unique request ID for tracking
        request_id = str(uuid.uuid4())
        self.request_ids[request_id] = True
        
        # Prepare headers with authentication
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "PlainSpeak/0.1.0",
            "X-Request-ID": request_id
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        # Add request ID to payload for tracing
        payload["request_id"] = request_id
        
        # Full URL
        url = f"{self.api_endpoint.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Try the request with retries
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
                
                # Check if the request was successful
                response.raise_for_status()
                
                # Parse and return response
                return response.json()
                
            except requests.RequestException as e:
                last_error = str(e)
                self.logger.warning(f"API request failed (attempt {attempt+1}/{self.retry_count}): {last_error}")
                
                # Don't retry certain errors
                if isinstance(e, requests.HTTPError) and e.response.status_code in (401, 403):
                    break
                    
        # If we get here, all retries failed
        error_msg = f"API request failed after {self.retry_count} attempts: {last_error}"
        self.logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    @lru_cache(maxsize=128)
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
            # Prepare request payload
            payload = {
                "text": text,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API request
            response = self._make_api_request("parse", payload)
            
            # Check if the response contains the expected fields
            if "verb" in response and "args" in response:
                return response
                
            # If response format is incorrect, log warning and fall back
            self.logger.warning(f"Unexpected API response format: {response}")
            return self._simple_parse(text)
            
        except Exception as e:
            self.logger.error(f"Error parsing natural language: {e}")
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
            # Prepare request payload
            payload = {
                "text": text,
                "locale": locale,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API request
            response = self._make_api_request("parse_with_locale", payload)
            
            # Check if the response contains the expected fields
            if "verb" in response and "args" in response:
                return response
                
            # If response format is incorrect, log warning and fall back
            self.logger.warning(f"Unexpected API response format: {response}")
            return self._simple_parse(text)
            
        except Exception as e:
            self.logger.error(f"Error parsing natural language with locale: {e}")
            # Fall back to simple parsing on error
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
        try:
            # Prepare request payload
            payload = {
                "query": query,
                "feedback_data": feedback_data,
                "previous_commands": previous_commands,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API request
            response = self._make_api_request("improve_command", payload)
            
            # Check if the response contains the expected field
            if "command" in response and isinstance(response["command"], str):
                return response["command"]
                
            # If response format is incorrect, log warning and fall back
            self.logger.warning(f"Unexpected API response format: {response}")
            
        except Exception as e:
            self.logger.error(f"Error getting improved command: {e}")
            
        # Fall back to default implementation
        if "corrected_command" in feedback_data:
            return feedback_data["corrected_command"]
            
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
        try:
            # Prepare request payload
            payload = {
                "text": text,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # Make API request
            response = self._make_api_request("suggest_verbs", payload)
            
            # Check if the response contains the expected field
            if "verbs" in response and isinstance(response["verbs"], list):
                return response["verbs"]
                
            # If response format is incorrect, log warning and fall back
            self.logger.warning(f"Unexpected API response format: {response}")
            
        except Exception as e:
            self.logger.error(f"Error suggesting verbs: {e}")
            
        # Fall back to default implementation
        common_verbs = [
            "list", "find", "search", "show", "create", "edit",
            "delete", "copy", "move", "rename", "download"
        ]
        
        # Filter verbs that match the beginning of the text
        if text:
            text_lower = text.lower()
            return [verb for verb in common_verbs if verb.startswith(text_lower)]
            
        return common_verbs 