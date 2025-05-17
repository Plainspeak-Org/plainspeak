"""
Command Parser for PlainSpeak.

This module handles the parsing of natural language into shell commands
using the LLM interface and prompt templates.
"""

import time
from typing import Optional, Dict, Any, Tuple, Union, List, cast
from datetime import datetime
import logging
from pathlib import Path

from .llm_interface import LLMInterface
from .prompts import get_shell_command_prompt
from .context import session_context
from .plugins.manager import plugin_manager
from .learning import learning_store, FeedbackEntry
from .ast import ast_builder, Command, Pipeline, CommandType, ArgumentType

logger = logging.getLogger(__name__)

# Define a common return type for parse methods
ParseResult = Union[Tuple[bool, str], Command, Pipeline]


class CommandParser:
    """
    Parses natural language into shell commands using an LLM.
    """

    def __init__(
        self,
        llm: Optional[LLMInterface] = None,
        generation_params: Optional[Dict[str, Any]] = None,
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
            "stop": ["\n"],  # Stop at newline since we want single commands
        }

    def _get_system_context(self) -> str:
        """
        Get the current system context for better command generation.

        Returns:
            str: Description of the current system environment.
        """
        # Use the session context to get a rich context for the LLM
        return session_context.get_context_for_llm()

    def parse_to_ast(self, input_text: str) -> ParseResult:  # type: ignore[return]
        """
        Parse natural language input into an AST.

        Args:
            input_text (str): Natural language description of the desired command.

        Returns:
            Either a Command/Pipeline object or a tuple with error info.
        """
        if not input_text.strip():
            return False, "ERROR: Empty input"

        # Try to find similar examples from learning store
        similar = learning_store.get_similar_examples(input_text, limit=3)
        if similar:
            # Use the highest-scoring match as a template
            template_text, template_cmd, score = similar[0]
            if score > 0.8:  # High confidence match
                try:
                    # Parse the template command into AST
                    ast = ast_builder.from_command_string(
                        template_cmd, original_text=input_text
                    )
                    # Add the original input text explicitly for both Command and Pipeline
                    if isinstance(ast, Command):
                        ast.input_text = input_text
                    elif isinstance(ast, Pipeline):
                        for cmd in ast.commands:
                            cmd.input_text = input_text
                    return ast
                except ValueError:
                    pass  # Fall through to other methods

        # Get system-specific context
        context = self._get_system_context()

        start_time = time.time()

        # Try parsing with plugin system
        try:
            ast = ast_builder.from_natural_language(
                input_text, {"context": context, "similar_examples": similar}
            )
            return ast
        except ValueError:
            pass  # Fall through to LLM method

        # Generate command using LLM
        prompt = get_shell_command_prompt(input_text, context)
        generated = self.llm.generate(prompt, **self.generation_params)

        if generated is None or generated.strip().startswith("ERROR:"):
            elapsed = time.time() - start_time
            learning_store.record_feedback(
                FeedbackEntry(
                    original_text=input_text,
                    generated_command="",
                    final_command=None,
                    success=False,
                    error_message="Failed to generate command",
                    execution_time=elapsed,
                    feedback_type="reject",
                    timestamp=datetime.now(),
                )
            )
            return False, "Failed to generate command"

        command = generated.strip()
        try:
            ast = ast_builder.from_command_string(command, original_text=input_text)
            elapsed = time.time() - start_time
            learning_store.record_feedback(
                FeedbackEntry(
                    original_text=input_text,
                    generated_command=command,
                    final_command=command,
                    success=True,
                    error_message=None,
                    execution_time=elapsed,
                    feedback_type="accept",
                    timestamp=datetime.now(),
                )
            )
            return ast
        except ValueError as e:
            elapsed = time.time() - start_time
            learning_store.record_feedback(
                FeedbackEntry(
                    original_text=input_text,
                    generated_command=command,
                    final_command=None,
                    success=False,
                    error_message=str(e),
                    execution_time=elapsed,
                    feedback_type="reject",
                    timestamp=datetime.now(),
                )
            )
            return False, f"ERROR: {str(e)}"

    def parse_to_command(self, text: str) -> Tuple[bool, str]:
        """
        Parse natural language into a shell command.

        Args:
            text: The natural language description.

        Returns:
            A tuple of (success, result) where result is either a command or error message.
        """
        # Sanitize input
        if not text.strip():
            return False, "Error: Empty input"

        try:
            # Generate command using LLM
            command = self.llm.generate_command(text)
            if not command:
                return False, "Error: Failed to generate command"

            # Return successful result
            return True, command if command is not None else ""
        except Exception as e:
            return False, f"Error: {str(e)}"

    def parse_command_output(
        self, command_obj: Union[Command, Pipeline], output: str
    ) -> str:
        """
        Parse command output into natural language.

        Args:
            command_obj: The command that generated the output.
            output: The output to parse.

        Returns:
            Natural language description of the output.
        """
        # Extract input text from either Command or Pipeline
        input_text: str = ""
        if isinstance(command_obj, Command):
            if command_obj.input_text is not None:
                input_text = command_obj.input_text
        elif isinstance(command_obj, Pipeline) and command_obj.commands:
            first_command = command_obj.commands[0]
            if first_command.input_text is not None:
                input_text = first_command.input_text

        # For simplicity, we'll just return the output for now
        return output
