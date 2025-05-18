"""
LLM Interface for PlainSpeak.

This module provides an interface for interacting with language models
for natural language understanding and generation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


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
