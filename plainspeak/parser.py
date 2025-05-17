"""
Command Parser for PlainSpeak.

This module handles the parsing of natural language into shell commands
using the LLM interface and prompt templates.
"""
import time
from typing import Optional, Dict, Any, Tuple, Union
from datetime import datetime

from .llm_interface import LLMInterface
from .prompts import get_shell_command_prompt
from .context import session_context
from .plugins.manager import plugin_manager
from .learning import learning_store, FeedbackEntry
from .ast import ast_builder, Command, Pipeline, CommandType, ArgumentType


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
        # Use the session context to get a rich context for the LLM
        return session_context.get_context_for_llm()

    def parse_to_ast(self, input_text: str) -> Union[Command, Pipeline]:
        """
        Parse natural language input into an AST.

        Args:
            input_text (str): Natural language description of the desired command.

        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if parsing succeeded, False if it failed or was unsafe
                - str: The generated command if successful, or an error message if not
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
                        template_cmd,
                        original_text=template_text
                    )
                    ast.input_text = input_text
                    return ast
                except ValueError:
                    pass  # Fall through to other methods

        # Get system-specific context
        context = self._get_system_context()

        start_time = time.time()
        
        # Try parsing with plugin system
        try:
            ast = ast_builder.from_natural_language(input_text, {
                "context": context,
                "similar_examples": similar
            })
            return ast
        except ValueError:
            pass  # Fall through to LLM method
            
        # Generate command using LLM
        prompt = get_shell_command_prompt(input_text, context)
        generated = self.llm.generate(prompt, **self.generation_params)
        
        if generated is None or generated.strip().startswith("ERROR:"):
            elapsed = time.time() - start_time
            learning_store.record_feedback(FeedbackEntry(
                original_text=input_text,
                generated_command="",
                final_command=None,
                success=False,
                error_message="Failed to generate command",
                execution_time=elapsed,
                feedback_type="reject",
                timestamp=datetime.now()
            ))
            raise ValueError("Failed to generate command")

        command = generated.strip()
        try:
            ast = ast_builder.from_command_string(command, original_text=input_text)
            elapsed = time.time() - start_time
            learning_store.record_feedback(FeedbackEntry(
                original_text=input_text,
                generated_command=command,
                final_command=command,
                success=True,
                error_message=None,
                execution_time=elapsed,
                feedback_type="accept",
                timestamp=datetime.now()
            ))
            return ast
        except ValueError as e:
            elapsed = time.time() - start_time
            learning_store.record_feedback(FeedbackEntry(
                original_text=input_text,
                generated_command=command,
                final_command=None,
                success=False,
                error_message=str(e),
                execution_time=elapsed,
                feedback_type="reject",
                timestamp=datetime.now()
            ))
            raise
            
    def parse_to_command(self, input_text: str) -> Tuple[bool, str]:
        """
        Parse natural language input into a shell command.
        
        This is the legacy interface, using the new AST-based parsing internally.
        """
        try:
            ast = self.parse_to_ast(input_text)
            if isinstance(ast, Pipeline):
                # Join pipeline commands with pipes
                return True, " | ".join(
                    plugin_manager.generate_command(cmd.name, {
                        arg.name: arg.value for arg in cmd.args if arg.name
                    })[1] for cmd in ast.commands
                )
            elif isinstance(ast, Command):
                if ast.type == CommandType.PLUGIN:
                    # Use plugin to generate final command
                    return plugin_manager.generate_command(
                        ast.name,
                        {arg.name: arg.value for arg in ast.args if arg.name}
                    )
                else:
                    # Reconstruct shell command
                    cmd_parts = [ast.name]
                    for arg in ast.args:
                        if arg.type == ArgumentType.OPTION:
                            cmd_parts.append(f"--{arg.name}={arg.value}")
                        elif arg.type == ArgumentType.FLAG:
                            cmd_parts.append(f"-{arg.value}")
                        else:
                            cmd_parts.append(str(arg.value))
                    return True, " ".join(cmd_parts)
        except ValueError as e:
            return False, f"ERROR: {str(e)}"
