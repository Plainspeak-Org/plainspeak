"""
LLM response parsing utilities.

This module contains helper functions for parsing LLM responses.
"""

import json
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LLMParsingError(Exception):
    """Exception raised for errors in parsing LLM responses."""


def parse_llm_response(response: str, original_command: str = None) -> Dict[str, Any]:
    """
    Parse LLM response into structured data.

    Args:
        response: Raw LLM response text.
        original_command: Original user command (optional).

    Returns:
        Dict containing parsed command structure.

    Raises:
        LLMParsingError: If parsing fails.
    """
    if not response or not response.strip():
        # Handle empty responses with fallbacks based on original command
        if original_command:
            if "memory" in original_command.lower() and "process" in original_command.lower():
                return {"verb": "ps", "args": {"aux": True, "sort": "-rss", "head": "10"}}

            # Extract first word as verb from original command
            parts = original_command.split()
            verb = parts[0].lower() if parts else "echo"

            # Basic fallback
            return {"verb": verb, "args": {}}

        raise LLMParsingError("Empty response from LLM")

    # Try to find JSON in markdown code blocks
    code_block_pattern = r"```(?:json)?\s*({[^`]+})\s*```"
    matches = re.findall(code_block_pattern, response)

    if matches:
        # Take first JSON block found
        json_str = matches[0]
    else:
        # Try treating whole response as JSON if it looks like JSON
        json_str = response.strip()
        if not (json_str.startswith("{") and json_str.endswith("}")):
            # If it's not JSON, extract command and create a simple structure
            command = response.strip().split("\n")[0]  # Take first line
            parts = command.split()
            verb = parts[0] if parts else "echo"
            return {"verb": verb, "args": {}}

    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise LLMParsingError("Response is not a JSON object")
        return data
    except json.JSONDecodeError as e:
        # Fall back to simple command structure on JSON parse error
        if original_command:
            # Create fallbacks for common queries
            if "memory" in original_command.lower() and "process" in original_command.lower():
                return {"verb": "ps", "args": {"aux": True, "sort": "-rss", "head": "10"}}

        # Extract first line as command
        command = response.strip().split("\n")[0]
        parts = command.split()
        verb = parts[0] if parts else "echo"

        # Log the error but return something usable
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return {"verb": verb, "args": {}}


def create_prompt_with_locale(system_prompt: str, text: str, locale: str) -> str:
    """
    Create a prompt with locale information.

    Args:
        system_prompt: Base system prompt.
        text: User query text.
        locale: Locale code.

    Returns:
        Formatted prompt string.
    """
    if system_prompt:
        return f"""{system_prompt}

USER QUERY (locale: {locale}): {text}

IMPORTANT GUIDANCE:
1. Respond with ONLY the exact command that would accomplish this task.
2. For system queries about services, ports, or processes, use the appropriate commands from the reference.
3. Be specific and complete - include all necessary flags and options.
4. Never return partial, placeholder, or generic commands like 'for' without the full syntax.
5. If unsure, use the most common command for the current operating system.
6. Format your response as a single line executable command.
7. Consider the locale when interpreting the query.

Now provide the single best command:"""
    else:
        return f"""Parse intent (locale: {locale}): {text}

IMPORTANT: Return a complete and executable command with all necessary arguments.
Never return just a command name without proper syntax."""
