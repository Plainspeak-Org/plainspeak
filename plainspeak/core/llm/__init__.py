"""LLM interface implementations."""

import logging

from .base import LLMInterface, LLMResponseError
from .local import LocalLLMInterface
from .remote import RemoteLLM, RemoteLLMInterface

logger = logging.getLogger(__name__)


def get_llm_interface(config=None) -> LLMInterface:
    """
    Factory function to get appropriate LLM interface.

    Args:
        config: Optional config object.

    Returns:
        LLM interface instance.
    """
    if not config or not hasattr(config.llm, "provider"):
        return RemoteLLMInterface(config)  # Default to remote

    provider = config.llm.provider.lower()
    if provider == "local":
        return LocalLLMInterface(config)
    elif provider in ("remote", "openai"):
        return RemoteLLMInterface(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# Export the key classes and functions
__all__ = [
    "LLMInterface",
    "LLMResponseError",
    "LocalLLMInterface",
    "RemoteLLMInterface",
    "RemoteLLM",
    "get_llm_interface",
]
