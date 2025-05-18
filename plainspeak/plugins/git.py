"""
Git Plugin for PlainSpeak.

This module provides Git version control operations through natural language.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict

from .base import YAMLPlugin, registry
from .platform import platform_manager


class GitPlugin(YAMLPlugin):
    """
    Plugin for Git operations.

    Features:
    - Basic repository operations (init, clone, status)
    - Branch management (create, switch, merge)
    - Change management (add, commit, push, pull)
    - Repository inspection (status, log)
    """

    def __init__(self):
        """Initialize the Git plugin."""
        yaml_path = Path(__file__).parent / "git.yaml"
        super().__init__(yaml_path)

        # Check if git is installed and get version
        try:
            version = subprocess.check_output(["git", "--version"], text=True).strip()
            self.git_version = version.split()[-1]
        except (subprocess.SubprocessError, OSError):
            raise RuntimeError("Git is not installed or not accessible. " "Please install Git >= 2.0.0")

    def _preprocess_args(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess command arguments.

        Args:
            verb: The verb being used.
            args: Original arguments.

        Returns:
            Processed arguments.
        """
        processed = args.copy()

        # Handle paths with platform-specific normalization
        path_args = ["path"]
        for arg in path_args:
            if arg in processed:
                path = processed[arg]
                if path:
                    processed[arg] = platform_manager.convert_path_for_command(path)

        # Handle URLs for clone
        if verb == "git-clone" and "url" in processed:
            url = processed["url"]
            # Extract URL from natural text if needed
            if "github.com" in url:
                # Try to extract full URL
                import re

                matches = re.findall(
                    r"https://github\.com/[\w\-]+/[\w\-]+(?:\.git)?|" r"git@github\.com:[\w\-]+/[\w\-]+(?:\.git)?",
                    url,
                )
                if matches:
                    processed["url"] = matches[0]

        # Handle commit messages
        if verb == "git-commit" and "message" in processed:
            msg = processed["message"]
            # Clean up message - remove quotes if they exist
            msg = msg.strip("'\"")
            processed["message"] = msg

        return processed

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a Git command.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """
        # Preprocess arguments
        args = self._preprocess_args(verb, args)

        # Special handling for common cases
        if verb == "git-add" and "path" not in args:
            # Default to adding all changes
            args["path"] = "."

        if verb == "git-status" and not args:
            # Default to normal (not short) status
            args["short"] = False

        if verb == "git-push" and not args:
            # Default to pushing current branch to origin
            args["remote"] = "origin"

        if verb == "git-pull" and not args:
            # Default to pulling from origin
            args["remote"] = "origin"

        # Generate command using parent's implementation
        return super().generate_command(verb, args)

    def _check_in_git_repo(self) -> bool:
        """
        Check if current directory is in a Git repository.

        Returns:
            True if in a Git repo, False otherwise.
        """
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return True
        except subprocess.SubprocessError:
            return False


# Create and register the plugin instance
try:
    git_plugin = GitPlugin()
    registry.register(git_plugin)
except (RuntimeError, ValueError) as e:
    # Log error but don't prevent other plugins from loading
    import logging

    logger = logging.getLogger(__name__)
    logger.warning("Failed to load Git plugin: %s", str(e))
