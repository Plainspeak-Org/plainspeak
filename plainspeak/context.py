"""
Contextual Understanding for PlainSpeak.

This module manages the session state and contextual information
that enhances the natural language understanding capabilities.
"""

import getpass
import json
import os
import platform
import socket
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from plainspeak.core.i18n import I18n
from plainspeak.core.llm import LLMInterface


class SessionContext:
    """
    Manages the session state and contextual information for PlainSpeak.

    This class tracks:
    - Environment variables
    - Current working directory
    - System information
    - Command history
    - User preferences
    - Session-specific variables
    - LLM interface and i18n settings
    """

    llm_interface: Optional[LLMInterface]
    i18n: Optional[I18n]
    parser: Optional[Any]

    def __init__(self, context_file_or_config=None):
        """
        Initialize the session context.

        Args:
            context_file_or_config: Either a Path to a context file or a config object.
                                    If config object is provided, context_file is set to None.
        """
        # Handle case where config object is passed instead of context_file
        if context_file_or_config is not None and not isinstance(context_file_or_config, Path):
            # This is likely a config object; just ignore it
            self.context_file = None
        else:
            self.context_file = context_file_or_config

        self._session_vars: Dict[str, Any] = {}
        self._command_history: list[Dict[str, Any]] = []
        self.llm_interface = None  # Will be set by the application
        self.i18n = None  # Will be set by the application
        self.parser = None  # Will be set by the application
        self._load_context()

    def _load_context(self) -> None:
        """Load context from file if it exists."""
        if self.context_file and self.context_file.exists():
            try:
                with open(self.context_file, "r") as f:
                    data = json.load(f)
                    self._session_vars = data.get("session_vars", {})
                    self._command_history = data.get("command_history", [])
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load context from {self.context_file}: {e}")

    def save_context(self) -> None:
        """Save context to file if a context file is specified."""
        if self.context_file:
            try:
                # Ensure directory exists
                self.context_file.parent.mkdir(parents=True, exist_ok=True)

                with open(self.context_file, "w") as f:
                    json.dump(
                        {
                            "session_vars": self._session_vars,
                            "command_history": self._command_history,
                        },
                        f,
                        indent=2,
                    )
            except IOError as e:
                print(f"Warning: Failed to save context to {self.context_file}: {e}")

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get current system information.

        Returns:
            Dict containing system information.
        """
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count() or 0,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
        }

    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get current environment information.

        Returns:
            Dict containing environment information.
        """
        return {
            "cwd": os.getcwd(),
            "home": str(Path.home()),
            "shell": os.environ.get("SHELL", ""),
            "path": os.environ.get("PATH", ""),
            "term": os.environ.get("TERM", ""),
        }

    def add_to_history(self, natural_text: str, command: str, success: bool) -> None:
        """
        Add a command to the history.

        Args:
            natural_text: The natural language input.
            command: The generated command.
            success: Whether the command was successfully executed.
        """
        self._command_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "natural_text": natural_text,
                "command": command,
                "success": success,
            }
        )

        # Limit history size to prevent unbounded growth
        if len(self._command_history) > 1000:
            self._command_history = self._command_history[-1000:]

        # Save after each addition to ensure we don't lose history
        self.save_context()

    def get_history(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get the command history.

        Args:
            limit: Maximum number of history items to return.

        Returns:
            List of history items, most recent first.
        """
        return self._command_history[-limit:][::-1]

    def set_session_var(self, key: str, value: Any) -> None:
        """
        Set a session variable.

        Args:
            key: Variable name.
            value: Variable value.
        """
        self._session_vars[key] = value
        self.save_context()

    def get_session_var(self, key: str, default: Any = None) -> Any:
        """
        Get a session variable.

        Args:
            key: Variable name.
            default: Default value if variable doesn't exist.

        Returns:
            Variable value or default.
        """
        return self._session_vars.get(key, default)

    def get_all_session_vars(self) -> Dict[str, Any]:
        """
        Get all session variables.

        Returns:
            Dict of all session variables.
        """
        return self._session_vars.copy()

    def get_llm_instruction(self) -> Optional[str]:
        """
        Get the LLM instruction string from session variables or a default.

        Returns:
            The LLM instruction string or None if not set.
        """
        return self.get_session_var("llm_instruction")

    def set_working_dir(self, path: str) -> bool:
        """
        Set the current working directory.

        Args:
            path: The new working directory path.

        Returns:
            True if successful, False otherwise.
        """
        try:
            expanded_path = os.path.expanduser(path)
            os.chdir(expanded_path)
            # Update any internal tracking of CWD if necessary, though get_environment_info() reads it dynamically.
            self.set_session_var("last_known_cwd", os.getcwd())  # Optionally track
            return True
        except FileNotFoundError:
            print(f"Error: Directory not found: {path}")
            return False
        except Exception as e:
            print(f"Error changing directory to {path}: {e}")
            return False

    def get_full_context(self) -> Dict[str, Any]:
        """
        Get the full context including system info, environment, and session vars.

        Returns:
            Dict containing all context information.
        """
        return {
            "system": self.get_system_info(),
            "environment": self.get_environment_info(),
            "session_vars": self.get_all_session_vars(),
            "history_size": len(self._command_history),
        }

    def get_context_for_llm(self) -> str:
        """
        Get a formatted string representation of the context for the LLM.

        Returns:
            String containing relevant context for the LLM.
        """
        env = self.get_environment_info()
        sys_info = self.get_system_info()

        context_str = f"""
Operating System: {sys_info['os']} ({sys_info['os_version']})
Current Directory: {env['cwd']}
Shell: {env['shell']}
Recent Commands: {len(self._command_history)} in history
"""

        # Add session variables if they exist
        if self._session_vars:
            context_str += "\nSession Variables:\n"
            for key, value in self._session_vars.items():
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 50:
                    str_value = str_value[:47] + "..."
                context_str += f"- {key}: {str_value}\n"

        return context_str.strip()


# For backwards compatibility with tests
PlainSpeakContext = SessionContext

# Default context instance
default_context_file = Path.home() / ".config" / "plainspeak" / "context.json"
session_context = SessionContext(default_context_file)


if __name__ == "__main__":
    # Example usage
    context = SessionContext()
    print("System Info:", context.get_system_info())
    print("Environment Info:", context.get_environment_info())
    print("Full Context for LLM:", context.get_context_for_llm())

    # Example of adding to history
    context.add_to_history("list all files in the current directory", "ls -la", True)

    print("History:", context.get_history())
