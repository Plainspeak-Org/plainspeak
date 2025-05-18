"""
LLM Interface for PlainSpeak.

This module provides an interface for interacting with language models
for natural language understanding and generation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMResponseError(Exception):
    """Raised when an error occurs during LLM response generation."""


class RemoteLLM(ABC):
    """Interface for remote LLM implementations."""

    @abstractmethod
    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        """Initialize with endpoint and optional API key."""

    @abstractmethod
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse natural language into a structured format."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text from a prompt."""

    def close(self) -> None:
        """Clean up any resources."""


class LLMInterface(ABC):
    """Base interface for language model interaction."""

    @abstractmethod
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse natural language into a structured format."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text from a prompt."""

    def close(self) -> None:
        """Clean up any resources."""

    def __del__(self) -> None:
        """Ensure resources are cleaned up."""
        try:
            self.close()
        except (AttributeError, TypeError) as e:
            # Log specific errors that could occur during cleanup
            logging.debug(f"Error during session cleanup: {e}")


class LocalLLMInterface(LLMInterface):
    """Interface for local LLM implementations."""

    def __init__(self, model_path: str):
        """Initialize with local model path."""
        self.model_path = model_path

    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse natural language into a structured format."""
        raise NotImplementedError("Local LLM implementation required")

    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text from a prompt."""
        raise NotImplementedError("Local LLM implementation required")


class RemoteLLMInterface(LLMInterface):
    """Interface for remote LLM implementations."""

    def __init__(self, endpoint: str, api_key: Optional[str] = None):
        """Initialize with endpoint and optional API key."""
        self.endpoint = endpoint
        self.api_key = api_key

    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse natural language into a structured format."""
        raise NotImplementedError("Remote LLM implementation required")

    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Generate text from a prompt."""
        raise NotImplementedError("Remote LLM implementation required")
