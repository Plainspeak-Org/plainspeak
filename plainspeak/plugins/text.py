"""
Text Plugin for PlainSpeak.

This plugin provides text operations like grep, sed, awk, etc.
"""

from typing import Any, Dict, List

from .base import Plugin, registry


class TextPlugin(Plugin):
    """
    Plugin for text operations.

    Provides verbs for:
    - grep: Search for patterns in text
    - sed: Stream editor for filtering and transforming text
    - awk: Pattern scanning and processing language
    - sort: Sort lines of text
    - uniq: Report or omit repeated lines
    - wc: Count lines, words, and characters
    - head: Output the first part of files
    - tail: Output the last part of files
    - cut: Remove sections from each line of files
    - tr: Translate or delete characters
    """

    def __init__(self):
        """Initialize the text plugin."""
        super().__init__(
            name="text",
            description="Text operations like grep, sed, awk, etc.",
            priority=10,  # Set higher priority to win conflicts with FilePlugin
        )

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        return [
            "grep",
            "search",
            "find-text",
            "sed",
            "replace",
            "awk",
            "process",
            "sort",
            "uniq",
            "unique",
            "wc",
            "count",
            "head",
            "top",
            "tail",
            "bottom",
            "cut",
            "tr",
            "translate",
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

        # Grep
        if verb in ["grep", "search", "find-text"]:
            pattern = args.get("pattern", "")
            file = args.get("file", "")
            recursive = args.get("recursive", False)
            ignore_case = args.get("ignore_case", False)

            cmd = "grep"
            if recursive:
                cmd += " -r"
            if ignore_case:
                cmd += " -i"
            cmd += f" '{pattern}'"
            if file:
                cmd += f" {file}"
            return cmd

        # Sed
        elif verb in ["sed", "replace"]:
            pattern = args.get("pattern", "")
            replacement = args.get("replacement", "")
            file = args.get("file", "")
            global_replace = args.get("global", True)

            cmd = "sed"
            sed_pattern = f"s/{pattern}/{replacement}/"
            if global_replace:
                sed_pattern += "g"
            cmd += f" '{sed_pattern}'"
            if file:
                cmd += f" {file}"
            return cmd

        # Awk
        elif verb in ["awk", "process"]:
            pattern = args.get("pattern", "")
            action = args.get("action", "")
            file = args.get("file", "")

            cmd = "awk"
            if pattern and action:
                cmd += f" '{pattern} {action}'"
            elif pattern:
                cmd += f" '{pattern}'"
            elif action:
                cmd += f" '{action}'"
            if file:
                cmd += f" {file}"
            return cmd

        # Sort
        elif verb in ["sort"]:
            file = args.get("file", "")
            numeric = args.get("numeric", False)
            reverse = args.get("reverse", False)

            cmd = "sort"
            if numeric:
                cmd += " -n"
            if reverse:
                cmd += " -r"
            if file:
                cmd += f" {file}"
            return cmd

        # Uniq
        elif verb in ["uniq", "unique"]:
            file = args.get("file", "")
            count = args.get("count", False)

            cmd = "uniq"
            if count:
                cmd += " -c"
            if file:
                cmd += f" {file}"
            return cmd

        # Wc
        elif verb in ["wc", "count"]:
            file = args.get("file", "")
            lines = args.get("lines", False)
            words = args.get("words", False)
            chars = args.get("chars", False)

            cmd = "wc"
            if lines:
                cmd += " -l"
            if words:
                cmd += " -w"
            if chars:
                cmd += " -c"
            if file:
                cmd += f" {file}"
            return cmd

        # Head
        elif verb in ["head", "top"]:
            file = args.get("file", "")
            lines = args.get("lines", 10)

            cmd = "head"
            if lines != 10:
                cmd += f" -n {lines}"
            if file:
                cmd += f" {file}"
            return cmd

        # Tail
        elif verb in ["tail", "bottom"]:
            file = args.get("file", "")
            lines = args.get("lines", 10)
            follow = args.get("follow", False)

            cmd = "tail"
            if lines != 10:
                cmd += f" -n {lines}"
            if follow:
                cmd += " -f"
            if file:
                cmd += f" {file}"
            return cmd

        # Cut
        elif verb in ["cut"]:
            file = args.get("file", "")
            delimiter = args.get("delimiter", "")
            fields = args.get("fields", "")

            cmd = "cut"
            if delimiter:
                cmd += f" -d'{delimiter}'"
            if fields:
                cmd += f" -f{fields}"
            if file:
                cmd += f" {file}"
            return cmd

        # Tr
        elif verb in ["tr", "translate"]:
            set1 = args.get("set1", "")
            set2 = args.get("set2", "")
            delete = args.get("delete", False)

            cmd = "tr"
            if delete:
                cmd += " -d"
                cmd += f" '{set1}'"
            else:
                cmd += f" '{set1}' '{set2}'"
            return cmd

        # Unknown verb
        else:
            return f"echo 'Unknown text operation: {verb}'"


# Register the plugin
text_plugin = TextPlugin()
registry.register(text_plugin)
