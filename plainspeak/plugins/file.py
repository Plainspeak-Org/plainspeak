"""
File Plugin for PlainSpeak.

This plugin provides file operations like listing, copying, moving, etc.
"""

from typing import Any, Dict, List

from .base import Plugin, registry


class FilePlugin(Plugin):
    """
    Plugin for file operations.

    Provides verbs for:
    - list: List files in a directory
    - find: Find files matching a pattern
    - copy: Copy files
    - move: Move files
    - delete: Delete files
    - read: Read file content
    - create: Create a new file
    - zip: Compress files
    - unzip: Extract compressed files
    """

    def __init__(self):
        """Initialize the file plugin."""
        super().__init__(
            name="file",
            description="File operations like listing, copying, moving, etc.",
        )

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        return [
            "list",
            "ls",
            "dir",
            "find",
            "search",
            "copy",
            "cp",
            "move",
            "mv",
            "delete",
            "rm",
            "remove",
            "read",
            "cat",
            "create",
            "touch",
            "zip",
            "compress",
            "unzip",
            "extract",
        ]

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """
        Generate a command for the given verb and arguments.

        Args:
            verb: The verb to handle.
            args: Arguments for the verb.

        Returns:
            The generated command string.
        """
        verb = verb.lower()

        # List files
        if verb in ["list", "ls", "dir"]:
            path = args.get("path", ".")
            show_hidden = args.get("show_hidden", False)
            long_format = args.get("long_format", True)

            cmd = "ls"
            if long_format:
                cmd += " -l"
            if show_hidden:
                cmd += "a"
            cmd += f" {path}"
            return cmd

        # Find files
        elif verb in ["find", "search"]:
            path = args.get("path", ".")
            pattern = args.get("pattern", "*")
            type_filter = args.get("type", "")

            cmd = f"find {path}"
            if type_filter:
                cmd += f" -type {type_filter}"
            if pattern:
                cmd += f" -name '{pattern}'"
            return cmd

        # Copy files
        elif verb in ["copy", "cp"]:
            source = args.get("source", "")
            destination = args.get("destination", "")
            recursive = args.get("recursive", False)

            cmd = "cp"
            if recursive:
                cmd += " -r"
            cmd += f" {source} {destination}"
            return cmd

        # Move files
        elif verb in ["move", "mv"]:
            source = args.get("source", "")
            destination = args.get("destination", "")

            return f"mv {source} {destination}"

        # Delete files
        elif verb in ["delete", "rm", "remove"]:
            path = args.get("path", "")
            recursive = args.get("recursive", False)
            force = args.get("force", False)

            cmd = "rm"
            if recursive:
                cmd += " -r"
            if force:
                cmd += " -f"
            cmd += f" {path}"
            return cmd

        # Read file content
        elif verb in ["read", "cat"]:
            path = args.get("path", "")

            return f"cat {path}"

        # Create a new file
        elif verb in ["create", "touch"]:
            path = args.get("path", "")

            return f"touch {path}"

        # Compress files
        elif verb in ["zip", "compress"]:
            source = args.get("source", "")
            destination = args.get("destination", "")

            if not destination.endswith(".zip"):
                destination += ".zip"

            return f"zip -r {destination} {source}"

        # Extract compressed files
        elif verb in ["unzip", "extract"]:
            source = args.get("source", "")
            destination = args.get("destination", ".")

            if source.endswith(".zip"):
                return f"unzip {source} -d {destination}"
            elif source.endswith(".tar.gz") or source.endswith(".tgz"):
                return f"tar -xzf {source} -C {destination}"
            elif source.endswith(".tar"):
                return f"tar -xf {source} -C {destination}"
            else:
                return f"unzip {source} -d {destination}"

        # Unknown verb
        else:
            return f"echo 'Unknown file operation: {verb}'"


# Register the plugin
file_plugin = FilePlugin()
registry.register(file_plugin)
