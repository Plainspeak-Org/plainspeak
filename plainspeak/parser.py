"""
Command Parser for PlainSpeak.

This module handles the parsing of natural language into shell commands
using the LLM interface and prompt templates.
"""
from typing import Optional, Dict, Any, Tuple
import platform
import os

from .llm_interface import LLMInterface
from .prompts import get_shell_command_prompt


class CommandParser:
    """
    Parses natural language into shell commands using an LLM.
    """

    def __init__(
        self,
        llm: Optional[LLMInterface] = None,
        generation_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the command parser.

        Args:
            llm (Optional[LLMInterface]): LLM interface to use. If None, creates a new one.
            generation_params (Optional[Dict[str, Any]]): Parameters for text generation.
                Defaults to reasonable values for command generation.
        """
        self.llm = llm or LLMInterface()
        self.generation_params = generation_params or {
            "temperature": 0.2,  # Lower temperature for more deterministic outputs
            "max_new_tokens": 100,  # Commands are usually short
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "stop": ["\n"]  # Stop at newline since we want single commands
        }

    def _get_system_context(self) -> str:
        """
        Get the current system context for better command generation.

        Returns:
            str: Description of the current system environment.
        """
        os_type = platform.system().lower()
        if os_type == "darwin":
            os_type = "macOS"
        
        shell = os.environ.get("SHELL", "").lower()
        if "bash" in shell:
            shell_type = "Bash"
        elif "zsh" in shell:
            shell_type = "Zsh"
        elif "fish" in shell:
            shell_type = "Fish"
        else:
            shell_type = "standard shell"

        return f"{os_type} system using {shell_type}"

    def parse_to_command(self, input_text: str) -> Tuple[bool, str]:
        """
        Parse natural language input into a shell command.

        Args:
            input_text (str): Natural language description of the desired command.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if parsing succeeded, False if it failed or was unsafe
                - str: The generated command if successful, or an error message if not
        """
        if not input_text.strip():
            return False, "ERROR: Empty input"

        # Get system-specific context
        context = self._get_system_context()
        
        # Generate the full prompt using the template
        prompt = get_shell_command_prompt(input_text, context)
        
        # Get the command from the LLM
        result = self.llm.generate(prompt, **self.generation_params)
        
        if result is None:
            return False, "ERROR: Failed to generate command"

        # Clean up the result
        command = result.strip()
        
        # Check for error markers
        if command.startswith("ERROR:"):
            return False, command
            
        # Basic safety checks
        unsafe_patterns = [
            "rm -rf",  # Dangerous file deletion
            "mkfs",    # Filesystem formatting
            ">",       # Output redirection (for now)
            "sudo",    # Privilege escalation
            ";",       # Command chaining
            "&&",      # Command chaining
            "||",      # Command chaining
            "|",       # Pipes (for initial version)
            "`",       # Command substitution
            "$(",      # Command substitution
        ]
        
        for pattern in unsafe_patterns:
            if pattern in command:
                return False, f"ERROR: Generated command contains unsafe pattern: {pattern}"

        return True, command
