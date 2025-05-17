"""
Tests for the plugins module.
"""

import pytest
from pathlib import Path
from plainspeak.plugins.base import Plugin, YAMLPlugin, PluginRegistry
from plainspeak.plugins.manager import PluginManager
from plainspeak.plugins.file import FilePlugin
from plainspeak.plugins.system import SystemPlugin
from plainspeak.plugins.network import NetworkPlugin
from plainspeak.plugins.text import TextPlugin


class TestPlugin(Plugin):
    """Test plugin for testing."""

    def __init__(self):
        super().__init__("test", "Test plugin")

    def get_verbs(self):
        return ["test", "example"]

    def generate_command(self, verb, args):
        if verb == "test":
            return f"echo 'Testing with {args}'"
        elif verb == "example":
            return f"echo 'Example command'"
        return "echo 'Unknown command'"


def test_plugin_base():
    """Test the base Plugin class."""
    plugin = TestPlugin()

    assert plugin.name == "test"
    assert plugin.description == "Test plugin"
    assert "test" in plugin.get_verbs()
    assert "example" in plugin.get_verbs()

    assert plugin.can_handle("test")
    assert plugin.can_handle("example")
    assert not plugin.can_handle("unknown")

    assert (
        plugin.generate_command("test", {"arg": "value"})
        == "echo 'Testing with {'arg': 'value'}'"
    )
    assert plugin.generate_command("example", {}) == "echo 'Example command'"


def test_plugin_registry():
    """Test the PluginRegistry class."""
    registry = PluginRegistry()
    plugin = TestPlugin()

    registry.register(plugin)

    assert registry.get_plugin("test") == plugin
    assert registry.get_plugin("unknown") is None

    assert registry.get_plugin_for_verb("test") == plugin
    assert registry.get_plugin_for_verb("example") == plugin
    assert registry.get_plugin_for_verb("unknown") is None

    verbs = registry.get_all_verbs()
    assert "test" in verbs
    assert "example" in verbs
    assert verbs["test"] == "test"
    assert verbs["example"] == "test"


def test_file_plugin():
    """Test the FilePlugin class."""
    plugin = FilePlugin()

    assert plugin.name == "file"
    assert "list" in plugin.get_verbs()
    assert "find" in plugin.get_verbs()
    assert "copy" in plugin.get_verbs()

    # Test list command
    cmd = plugin.generate_command("list", {"path": "/tmp", "show_hidden": True})
    assert "ls" in cmd
    assert "-la" in cmd
    assert "/tmp" in cmd

    # Test find command
    cmd = plugin.generate_command("find", {"path": "/tmp", "pattern": "*.txt"})
    assert "find" in cmd
    assert "/tmp" in cmd
    assert "*.txt" in cmd

    # Test copy command
    cmd = plugin.generate_command(
        "copy", {"source": "file.txt", "destination": "/tmp/", "recursive": True}
    )
    assert "cp" in cmd
    assert "-r" in cmd
    assert "file.txt" in cmd
    assert "/tmp/" in cmd


def test_system_plugin():
    """Test the SystemPlugin class."""
    plugin = SystemPlugin()

    assert plugin.name == "system"
    assert "ps" in plugin.get_verbs()
    assert "df" in plugin.get_verbs()
    assert "uptime" in plugin.get_verbs()

    # Test ps command
    cmd = plugin.generate_command("ps", {"all": True})
    assert "ps" in cmd
    assert "aux" in cmd

    # Test df command
    cmd = plugin.generate_command("df", {"human_readable": True, "path": "/tmp"})
    assert "df" in cmd
    assert "-h" in cmd
    assert "/tmp" in cmd

    # Test uptime command
    cmd = plugin.generate_command("uptime", {"pretty": True})
    assert "uptime" in cmd
    assert "-p" in cmd


def test_network_plugin():
    """Test the NetworkPlugin class."""
    plugin = NetworkPlugin()

    assert plugin.name == "network"
    assert "ping" in plugin.get_verbs()
    assert "curl" in plugin.get_verbs()
    assert "ssh" in plugin.get_verbs()

    # Test ping command
    cmd = plugin.generate_command("ping", {"host": "example.com", "count": 5})
    assert "ping" in cmd
    assert "-c 5" in cmd
    assert "example.com" in cmd

    # Test curl command
    cmd = plugin.generate_command(
        "curl", {"url": "https://example.com", "output": "output.html"}
    )
    assert "curl" in cmd
    assert "-o output.html" in cmd
    assert "https://example.com" in cmd

    # Test ssh command
    cmd = plugin.generate_command(
        "ssh", {"host": "example.com", "user": "user", "port": 2222}
    )
    assert "ssh" in cmd
    assert "-p 2222" in cmd
    assert "user@example.com" in cmd


def test_text_plugin():
    """Test the TextPlugin class."""
    plugin = TextPlugin()

    assert plugin.name == "text"
    assert "grep" in plugin.get_verbs()
    assert "sed" in plugin.get_verbs()
    assert "wc" in plugin.get_verbs()

    # Test grep command
    cmd = plugin.generate_command(
        "grep", {"pattern": "error", "file": "log.txt", "recursive": True}
    )
    assert "grep" in cmd
    assert "-r" in cmd
    assert "'error'" in cmd
    assert "log.txt" in cmd

    # Test sed command
    cmd = plugin.generate_command(
        "sed", {"pattern": "old", "replacement": "new", "file": "file.txt"}
    )
    assert "sed" in cmd
    assert "s/old/new/g" in cmd
    assert "file.txt" in cmd

    # Test wc command
    cmd = plugin.generate_command("wc", {"file": "file.txt", "lines": True})
    assert "wc" in cmd
    assert "-l" in cmd
    assert "file.txt" in cmd


def test_plugin_manager():
    """Test the PluginManager class."""
    manager = PluginManager()

    # Test getting all plugins
    plugins = manager.get_all_plugins()
    assert "file" in plugins
    assert "system" in plugins
    assert "network" in plugins
    assert "text" in plugins

    # Test getting all verbs
    verbs = manager.get_all_verbs()
    assert "list" in verbs
    assert "ps" in verbs
    assert "ping" in verbs
    assert "grep" in verbs

    # Test getting plugin for verb
    assert manager.get_plugin_for_verb("list").name == "file"
    assert manager.get_plugin_for_verb("ps").name == "system"
    assert manager.get_plugin_for_verb("ping").name == "network"
    assert manager.get_plugin_for_verb("grep").name == "text"

    # Test generating command
    success, cmd = manager.generate_command("list", {"path": "/tmp"})
    assert success
    assert "ls" in cmd
    assert "/tmp" in cmd

    # Test extracting verb and args
    verb, args = manager.extract_verb_and_args("list /tmp")
    assert verb == "list"
    assert "path" in args
    assert args["path"] == "/tmp"

    verb, args = manager.extract_verb_and_args("grep error in log.txt")
    assert verb == "grep"
    assert (
        "text" in args or "path" in args
    )  # Simple parsing might put this in different args
