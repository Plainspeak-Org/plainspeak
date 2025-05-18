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
import time
import plainspeak


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
    
    This class calls a remote API for natural language processing with
    comprehensive security features including proper SSL verification,
    API key management, and request rate limiting.
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
        ssl_cert_path: Optional[str] = None,
        rate_limit_per_minute: int = 60,
        backoff_factor: float = 0.5,
        rotate_keys: bool = False,
        api_keys: Optional[List[str]] = None
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
            rate_limit_per_minute: Maximum number of requests per minute.
            backoff_factor: Exponential backoff factor for retries.
            rotate_keys: Whether to rotate API keys on failure.
            api_keys: List of API keys to rotate through if rotate_keys is True.
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_count = retry_count
        self.backoff_factor = backoff_factor
        self.rate_limit_per_minute = rate_limit_per_minute
        self.rotate_keys = rotate_keys
        self.api_keys = api_keys or []
        self.current_key_index = 0
        
        if self.rotate_keys and not self.api_keys and self.api_key:
            # If rotate_keys is enabled but no keys list is provided, add the single key
            self.api_keys = [self.api_key]
        
        # Configure SSL verification
        self.verify_ssl = certifi.where() if verify_ssl else False
        if ssl_cert_path and os.path.exists(ssl_cert_path):
            self.verify_ssl = ssl_cert_path
            
        # Setup logging
        self.logger = logging.getLogger("RemoteLLM")
        
        # Track API calls for rate limiting
        self.request_count = 0
        self.request_times: List[float] = []
        self.request_ids: Dict[str, bool] = {}
        
        # Create a session for connection pooling
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        # Track consecutive failures for circuit breaking
        self.consecutive_failures = 0
        self.circuit_open = False
        self.circuit_open_time = 0
        self.circuit_reset_timeout = 60  # Reset circuit after 60 seconds
        
    def _rotate_api_key(self) -> bool:
        """
        Rotate to the next API key in the list.
        
        Returns:
            True if rotation was successful, False otherwise.
        """
        if not self.rotate_keys or not self.api_keys:
            return False
            
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.api_key = self.api_keys[self.current_key_index]
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.logger.info(f"Rotated to API key {self.current_key_index + 1}/{len(self.api_keys)}")
        return True
    
    def _check_rate_limit(self) -> bool:
        """
        Check if the current request would exceed rate limits.
        
        Returns:
            True if the request is allowed, False if it would exceed limits.
        """
        if self.rate_limit_per_minute <= 0:
            return True
            
        # Remove request times older than 60 seconds
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # Check if we're under the limit
        if len(self.request_times) < self.rate_limit_per_minute:
            self.request_times.append(current_time)
            return True
            
        self.logger.warning(f"Rate limit exceeded: {len(self.request_times)} requests in the last minute")
        return False
    
    def _check_circuit_breaker(self) -> bool:
        """
        Check if the circuit breaker is open (preventing requests due to failures).
        
        Returns:
            True if requests can proceed, False if the circuit is open.
        """
        if not self.circuit_open:
            return True
            
        # Check if it's time to reset the circuit
        current_time = time.time()
        if current_time - self.circuit_open_time > self.circuit_reset_timeout:
            self.circuit_open = False
            self.consecutive_failures = 0
            self.logger.info("Circuit breaker reset")
            return True
            
        self.logger.warning("Circuit breaker open, request blocked")
        return False
        
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
        # Check circuit breaker
        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker open due to consecutive failures")
            
        # Check rate limiting
        if not self._check_rate_limit():
            raise RuntimeError("Rate limit exceeded")
        
        # Generate a unique request ID for tracking
        request_id = str(uuid.uuid4())
        self.request_ids[request_id] = True
        
        # Track request count for rate limiting
        self.request_count += 1
        
        # Prepare headers with authentication
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"PlainSpeak/{plainspeak.__version__}",
            "X-Request-ID": request_id
        }
        
        # Add request ID to payload for tracing
        payload["request_id"] = request_id
        
        # Full URL
        url = f"{self.api_endpoint.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Try the request with retries
        last_error = None
        rotated_key = False
        
        for attempt in range(self.retry_count):
            try:
                if attempt > 0:
                    # Exponential backoff
                    sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                    time.sleep(sleep_time)
                
                response = self.session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
                
                # Check if the request was successful
                response.raise_for_status()
                
                # Reset failure counter on success
                self.consecutive_failures = 0
                
                # Parse and return response
                try:
                    return response.json()
                except ValueError:
                    self.logger.warning(f"Invalid JSON response: {response.text[:100]}...")
                    raise RuntimeError("Invalid JSON response from API")
                
            except requests.RequestException as e:
                last_error = str(e)
                self.logger.warning(f"API request failed (attempt {attempt+1}/{self.retry_count}): {last_error}")
                
                self.consecutive_failures += 1
                
                # Open circuit breaker if too many consecutive failures
                if self.consecutive_failures >= 5:
                    self.circuit_open = True
                    self.circuit_open_time = time.time()
                    self.logger.warning("Circuit breaker opened due to consecutive failures")
                
                # Don't retry certain errors
                if isinstance(e, requests.HTTPError):
                    status_code = e.response.status_code
                    
                    # Authentication errors - try rotating API key
                    if status_code in (401, 403):
                        if not rotated_key and self.rotate_keys and self._rotate_api_key():
                            rotated_key = True
                            continue  # Try again with new key without counting as a retry
                        else:
                            break  # Don't retry auth errors if we can't rotate keys
                        
                    # Don't retry client errors except rate limiting
                    if 400 <= status_code < 500 and status_code != 429:
                        break
                    
                    # For rate limiting, wait longer
                    if status_code == 429:
                        retry_after = e.response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                sleep_time = float(retry_after)
                                time.sleep(min(sleep_time, 30))  # Cap at 30 seconds
                            except ValueError:
                                pass
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Unexpected error (attempt {attempt+1}/{self.retry_count}): {last_error}")
                self.consecutive_failures += 1
                    
        # If we get here, all retries failed
        error_msg = f"API request failed after {self.retry_count} attempts: {last_error}"
        self.logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    def close(self) -> None:
        """Close the session to free resources."""
        self.session.close()
        
    def __del__(self) -> None:
        """Ensure the session is closed when the object is garbage collected."""
        try:
            self.close()
        except:
            pass
    
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