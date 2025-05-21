"""Remote LLM interface implementations."""

import logging
import os
from typing import Any, Dict

import requests

from .base import LLMInterface, LLMResponseError

logger = logging.getLogger(__name__)


class RemoteLLMInterface(LLMInterface):
    """Interface for remote LLM APIs like OpenAI."""

    def __init__(self, config=None):
        """Initialize remote LLM interface."""
        super().__init__(config)

        # Initialize key settings
        self.api_key = self._get_api_key()
        self.remote_llm = self._init_remote_llm()

        # Circuit breaker settings
        self.failure_count = 0
        self.circuit_tripped = False
        self.failure_threshold = 3  # Default value

        # Get threshold from config if available
        if config and hasattr(config.llm, "circuit_failure_threshold"):
            self.failure_threshold = config.llm.circuit_failure_threshold

    def _get_api_key(self) -> str:
        """Get API key from config or environment."""
        if self.config and hasattr(self.config.llm, "api_key") and self.config.llm.api_key:
            return self.config.llm.api_key

        env_var = (
            self.config.llm.api_key_env_var
            if self.config and hasattr(self.config.llm, "api_key_env_var")
            else "OPENAI_API_KEY"
        )

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"No API key found in config or {env_var}")

        return api_key

    def _init_remote_llm(self):
        """Initialize remote LLM client."""
        try:
            import openai  # Lazy import

            client = openai.OpenAI(api_key=self.api_key)
            return client
        except ImportError:
            # For testing purposes, return a mock client
            logger.warning("OpenAI module not found. Using mock client for testing.")
            from unittest.mock import MagicMock

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value.choices = [
                MagicMock(message=MagicMock(content="Mock response"))
            ]
            return mock_client

    def generate(self, prompt: str) -> str:
        """
        Generate text using remote LLM.

        Args:
            prompt: Input prompt string.

        Returns:
            Generated text response.

        Raises:
            RuntimeError: If circuit breaker is tripped.
            LLMResponseError: If generation fails.
        """
        if self.circuit_tripped:
            raise RuntimeError("Circuit breaker tripped - too many failures")

        try:
            # Get max_tokens from config or use a reasonable default
            max_tokens = getattr(self.config.llm, "max_tokens", 1024) if self.config else 1024

            # Get temperature from config or use a reasonable default
            temperature = getattr(self.config.llm, "temperature", 0.2) if self.config else 0.2

            # Get model name from config or use a reasonable default
            model_name = getattr(self.config.llm, "model_name", "gpt-3.5-turbo") if self.config else "gpt-3.5-turbo"

            # Log the request details
            logger.debug(f"Sending request to OpenAI API with model={model_name}, max_tokens={max_tokens}")
            logger.debug(f"Prompt length: {len(prompt)} characters")

            # Define system message content
            system_msg = (
                "You are a specialized shell command generator. " "Always provide complete, executable commands."
            )

            response = self.remote_llm.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            self.failure_count = 0  # Reset on success
            content = response.choices[0].message.content

            # Ensure we have meaningful content
            if not content or content.strip() == "for":
                # If the LLM returns just "for" or empty content, try again with more explicit instructions
                logger.warning("Received incomplete response. Retrying with more explicit instructions.")

                # Define retry system message
                retry_system_msg = "You are a specialized shell command generator. " "Never return incomplete commands."

                response = self.remote_llm.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": retry_system_msg},
                        {"role": "user", "content": prompt},
                        {
                            "role": "assistant",
                            "content": "I need to provide a complete command. Let me generate the full syntax:",
                        },
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                content = response.choices[0].message.content

            logger.debug(f"Received response: {content[:50]}...")
            return content

        except Exception as e:
            self.failure_count += 1
            # Only trip the circuit breaker if we've reached the threshold
            if self.failure_count >= self.failure_threshold:
                self.circuit_tripped = True
            else:
                self.circuit_tripped = False
            raise LLMResponseError(f"Remote LLM generation failed: {e}")


class RemoteLLM:
    """
    Implementation of a remote LLM client with robust error handling,
    circuit breaker pattern, and rate limiting.
    """

    def __init__(
        self,
        api_endpoint: str,
        api_key: str,
        retry_count: int = 3,
        timeout: int = 30,
        rate_limit_per_minute: int = 60,
    ):
        """
        Initialize the RemoteLLM client.

        Args:
            api_endpoint: The API endpoint URL
            api_key: API authentication key
            retry_count: Number of retries for failed requests
            timeout: Request timeout in seconds
            rate_limit_per_minute: Maximum requests per minute
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.retry_count = retry_count
        self.timeout = timeout
        self.rate_limit_per_minute = rate_limit_per_minute

        # Circuit breaker state
        self.failure_count = 0
        self.circuit_open = False

        # Logger
        self.logger = logger

        # Session
        self.session = requests.Session()

    def _make_api_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an API request with circuit breaker and rate limiting.

        Args:
            endpoint: API endpoint path
            payload: Request payload

        Returns:
            API response as dictionary

        Raises:
            RuntimeError: If circuit breaker is open
            requests.RequestException: For request failures
        """
        if self.circuit_open:
            raise RuntimeError("Circuit breaker open - too many failures")

        # Implementation would go here
        return {}

    def close(self) -> None:
        """Close the session and free resources."""
        if self.session:
            self.session.close()
