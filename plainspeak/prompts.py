"""
Prompt templates for PlainSpeak.

This module contains the prompt templates used to interact with the LLM
for various tasks like shell command generation, API call creation, etc.
"""

# Base template for shell command generation.
# The template is formatted with:
# - {input_text}: The user's natural language request
# - {context}: Optional context about the current environment (e.g., OS type, current directory)
SHELL_COMMAND_TEMPLATE = """Given this request in plain English:
"{input_text}"

Generate a single shell command that accomplishes this task.
Additional context: {context}

Consider these guidelines:
1. Output ONLY the command, no explanations.
2. Use standard Unix/Linux shell syntax.
3. Use common utilities (ls, cp, mv, grep, etc.).
4. If the request is unclear or unsafe, output "ERROR: " followed by a brief reason.

Command:"""


def get_shell_command_prompt(input_text: str, context: str = "Unix-like environment") -> str:
    """
    Formats the shell command template with the given input text and context.

    Args:
        input_text (str): The user's natural language request.
        context (str): Optional context about the environment. Defaults to "Unix-like environment".

    Returns:
        str: The formatted prompt ready for the LLM.
    """
    return SHELL_COMMAND_TEMPLATE.format(input_text=input_text, context=context)
