"""
Network Plugin for PlainSpeak.

This plugin provides network operations like ping, curl, wget, etc.
"""

from typing import Any, Dict, List

from .base import Plugin, registry


class NetworkPlugin(Plugin):
    """
    Plugin for network operations.

    Provides verbs for:
    - ping: Check network connectivity
    - curl: Make HTTP requests
    - wget: Download files
    - ifconfig/ip: Show network interfaces
    - netstat: Show network connections
    - ssh: Connect to remote servers
    - scp: Copy files to/from remote servers
    - nslookup/dig: DNS lookup
    - traceroute: Trace network path
    - port: Check if a port is open
    """

    def __init__(self):
        """Initialize the network plugin."""
        super().__init__(name="network", description="Network operations like ping, curl, wget, etc.")

    def get_verbs(self) -> List[str]:
        """
        Get the list of verbs this plugin can handle.

        Returns:
            List of verb strings.
        """
        return [
            "ping",
            "check",
            "curl",
            "http",
            "request",
            "wget",
            "download",
            "ifconfig",
            "ip",
            "interfaces",
            "netstat",
            "connections",
            "ssh",
            "connect",
            "scp",
            "secure-copy",
            "nslookup",
            "dig",
            "dns",
            "traceroute",
            "trace",
            "port",
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

        # Ping
        if verb in ["ping", "check"]:
            # If args contains "port", handle this as port checking
            if "port" in args:
                return self._handle_port_check(args)

            host = args.get("host", "")
            count = args.get("count", "")

            cmd = "ping"
            if count:
                cmd += f" -c {count}"
            cmd += f" {host}"
            return cmd

        # Port checking
        elif verb == "port":
            return self._handle_port_check(args)

        # Curl
        elif verb in ["curl", "http", "request"]:
            url = args.get("url", "")
            method = args.get("method", "").upper()
            headers = args.get("headers", {})
            data = args.get("data", "")
            output = args.get("output", "")

            cmd = "curl"
            if method:
                cmd += f" -X {method}"
            for key, value in headers.items():
                cmd += f" -H '{key}: {value}'"
            if data:
                cmd += f" -d '{data}'"
            if output:
                cmd += f" -o {output}"
            cmd += f" {url}"
            return cmd

        # Wget
        elif verb in ["wget", "download"]:
            url = args.get("url", "")
            output = args.get("output", "")

            cmd = "wget"
            if output:
                cmd += f" -O {output}"
            cmd += f" {url}"
            return cmd

        # Network interfaces
        elif verb in ["ifconfig", "ip", "interfaces"]:
            interface = args.get("interface", "")

            if verb == "ifconfig":
                cmd = "ifconfig"
                if interface:
                    cmd += f" {interface}"
            else:
                cmd = "ip addr show"
                if interface:
                    cmd += f" {interface}"
            return cmd

        # Network connections
        elif verb in ["netstat", "connections"]:
            all_connections = args.get("all", True)
            listening = args.get("listening", False)

            cmd = "netstat"
            if all_connections:
                cmd += " -a"
            if listening:
                cmd += " -l"
            return cmd

        # SSH
        elif verb in ["ssh", "connect"]:
            host = args.get("host", "")
            user = args.get("user", "")
            port = args.get("port", "")
            key = args.get("key", "")

            cmd = "ssh"
            if port:
                cmd += f" -p {port}"
            if key:
                cmd += f" -i {key}"
            if user:
                cmd += f" {user}@{host}"
            else:
                cmd += f" {host}"
            return cmd

        # SCP
        elif verb in ["scp", "secure-copy"]:
            source = args.get("source", "")
            destination = args.get("destination", "")
            recursive = args.get("recursive", False)

            cmd = "scp"
            if recursive:
                cmd += " -r"
            cmd += f" {source} {destination}"
            return cmd

        # DNS lookup
        elif verb in ["nslookup", "dig", "dns"]:
            domain = args.get("domain", "")
            type_filter = args.get("type", "")

            if verb == "dig":
                cmd = "dig"
                if type_filter:
                    cmd += f" {type_filter}"
                cmd += f" {domain}"
            else:
                cmd = f"nslookup {domain}"
            return cmd

        # Traceroute
        elif verb in ["traceroute", "trace"]:
            host = args.get("host", "")

            return f"traceroute {host}"

        # Unknown verb
        else:
            return f"echo 'Unknown network operation: {verb}'"

    def _handle_port_check(self, args: Dict[str, Any]) -> str:
        """
        Handle port checking command.

        Args:
            args: Arguments for port checking.

        Returns:
            The generated command string.
        """
        host = args.get("host", "")
        port = args.get("port", "")

        # Use nc (netcat) for port checking if available
        return f"nc -zv {host} {port}"


# Register the plugin
network_plugin = NetworkPlugin()
registry.register(network_plugin)
