import logging
from typing import Any, Dict, Optional, Tuple

from plainspeak.config import AppConfig
from plainspeak.core.sandbox import Sandbox, SandboxExecutionError

logger = logging.getLogger(__name__)


class Commander:
    """
    The Commander is responsible for taking a fully resolved Abstract Syntax Tree (AST)
    and executing the command it represents, typically using a Sandbox.
    """

    def __init__(self, config: AppConfig, sandbox: Sandbox):
        self.config = config
        self.sandbox = sandbox

    def execute(self, ast: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """
        Executes the command defined in the AST.

        Args:
            ast: The Abstract Syntax Tree representing the command.
                 Expected keys include:
                 - 'command_template': The command string with placeholders.
                 - 'parameters': A dictionary of parameters to fill placeholders.
                 - 'action_type': The type of action (e.g., 'execute_command').
                 - 'plugin': Name of the plugin.
                 - 'verb': Name of the verb.

        Returns:
            A tuple (success: bool, output: str, error: Optional[str]).
            - success: True if execution was successful, False otherwise.
            - output: The standard output from the command.
            - error: The standard error from the command, or an error message.
        """
        logger.debug(f"Commander received AST for execution: {ast}")

        action_type = ast.get("action_type")
        command_template = ast.get("command_template")
        parameters = ast.get("parameters", {})

        if not command_template:
            logger.error("AST missing 'command_template' for execution.")
            return False, "", "Internal error: Command template missing in AST."

        if action_type == "execute_command":
            try:
                # Render the command
                final_command = command_template.format(**parameters)
                logger.info(f"Executing command: {final_command}")

                # Execute in sandbox
                return_code, stdout, stderr = self.sandbox.execute_shell_command(final_command)

                if return_code == 0:
                    logger.info(f"Command executed successfully. Output: {stdout[:200]}...")
                    # Ensure stdout is a string, not None
                    return True, stdout if stdout is not None else "", stderr
                else:
                    logger.warning(f"Command failed with return code {return_code}. Error: {stderr}")
                    return False, stdout if stdout is not None else "", stderr
            except KeyError as e:
                # This might happen if command_template has a placeholder not in parameters
                param_name = str(e).strip("'")
                logger.error(f"Missing parameter for command template: {param_name}. AST: {ast}")
                err_msg = f"Error rendering command: Missing parameter '{param_name}'."
                return False, "", err_msg
            except SandboxExecutionError as e:
                logger.error(f"Sandbox execution error: {e}")
                return False, "", str(e)
            except Exception as e:
                logger.exception(f"Unexpected error during command execution: {e}. AST: {ast}")
                return False, "", f"Unexpected error: {e}"
        # elif action_type == "api_call":
        # Placeholder for other action types
        # success, result = self._execute_api_call(ast)
        # return success, result, None if success else result
        else:
            logger.warning(f"Unsupported action_type '{action_type}' in AST.")
            return False, "", f"Unsupported action type: {action_type}"

    # def _execute_api_call(self, ast: Dict[str, Any]) -> Tuple[bool, str]:
    #     # Example:
    #     # plugin_name = ast.get("plugin")
    #     # verb_name = ast.get("verb")
    #     # params = ast.get("parameters")
    #     # ... logic to call a specific API via a plugin method or http client ...
    #     logger.error("API call execution not yet implemented.")
    #     return False, "API call execution not implemented."
