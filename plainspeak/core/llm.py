"""LLM interface implementations.

This module provides interfaces for local and remote LLM interactions.
It has been modularized into multiple sub-modules in the llm/ directory.
This file exists for backward compatibility.
"""

from .llm import get_llm_interface

# Re-export everything from the new llm package
from .llm.base import LLMInterface, LLMResponseError
from .llm.local import LocalLLMInterface
from .llm.remote import RemoteLLM, RemoteLLMInterface

# For backward compatibility
__all__ = [
    "LLMInterface",
    "LLMResponseError",
    "LocalLLMInterface",
    "RemoteLLMInterface",
    "RemoteLLM",
    "get_llm_interface",
]
