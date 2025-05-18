"""
System Plugin for PlainSpeak.

This plugin provides system operations like checking processes, disk usage, etc.
"""

from typing import Any, Dict, List

from .base import Plugin, registry


class SystemPlugin(Plugin):
    """
    Plugin for system operations.

    Provides verbs for:
    - ps: List processes
    - kill: Kill a process
    - df: Check disk usage
    - du: Check directory size
    - free: Check memory usage
    - top: Monitor system resources
    - uname: Show system information
    - date: Show or set date and time
    - uptime: Show system uptime
    - hostname: Show or set hostname
    """

    def __init__(self):
        """Initialize the system plugin."""
        super().__init__(
            name="system",
            description="System operations like checking processes, disk usage, etc.",
        )

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        return [
            "ps",
            "processes",
            "kill",
            "terminate",
            "df",
            "disk",
            "du",
            "size",
            "free",
            "memory",
            "top",
            "monitor",
            "uname",
            "system",
            "date",
            "time",
            "uptime",
            "hostname",
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

        # List processes
        if verb in ["ps", "processes"]:
            all_processes = args.get("all", True)
            full_format = args.get("full", False)

            cmd = "ps"
            if all_processes:
                cmd += " aux"
            elif full_format:
                cmd += " -ef"
            return cmd

        # Kill a process
        elif verb in ["kill", "terminate"]:
            pid = args.get("pid", "")
            signal = args.get("signal", "")
            force = args.get("force", False)

            cmd = "kill"
            if force:
                cmd += " -9"
            elif signal:
                cmd += f" -{signal}"
            cmd += f" {pid}"
            return cmd

        # Check disk usage
        elif verb in ["df", "disk"]:
            human_readable = args.get("human_readable", True)
            path = args.get("path", "")

            cmd = "df"
            if human_readable:
                cmd += " -h"
            if path:
                cmd += f" {path}"
            return cmd

        # Check directory size
        elif verb in ["du", "size"]:
            human_readable = args.get("human_readable", True)
            summarize = args.get("summarize", True)
            path = args.get("path", ".")

            cmd = "du"
            if human_readable:
                cmd += " -h"
            if summarize:
                cmd += " -s"
            cmd += f" {path}"
            return cmd

        # Check memory usage
        elif verb in ["free", "memory"]:
            human_readable = args.get("human_readable", True)

            cmd = "free"
            if human_readable:
                cmd += " -h"
            return cmd

        # Monitor system resources
        elif verb in ["top", "monitor"]:
            batch_mode = args.get("batch_mode", False)
            iterations = args.get("iterations", "")

            cmd = "top"
            if batch_mode:
                cmd += " -b"
                if iterations:
                    cmd += f" -n {iterations}"
            return cmd

        # Show system information
        elif verb in ["uname", "system"]:
            all_info = args.get("all", True)

            cmd = "uname"
            if all_info:
                cmd += " -a"
            return cmd

        # Show or set date and time
        elif verb in ["date", "time"]:
            format_str = args.get("format", "")
            set_time = args.get("set", "")

            cmd = "date"
            if format_str:
                cmd += f" +'{format_str}'"
            elif set_time:
                cmd += f" -s '{set_time}'"
            return cmd

        # Show system uptime
        elif verb in ["uptime"]:
            pretty = args.get("pretty", False)

            cmd = "uptime"
            if pretty:
                cmd += " -p"
            return cmd

        # Show or set hostname
        elif verb in ["hostname"]:
            set_name = args.get("set", "")

            cmd = "hostname"
            if set_name:
                cmd += f" {set_name}"
            return cmd

        # Unknown verb
        else:
            return f"echo 'Unknown system operation: {verb}'"


# Register the plugin
system_plugin = SystemPlugin()
registry.register(system_plugin)
