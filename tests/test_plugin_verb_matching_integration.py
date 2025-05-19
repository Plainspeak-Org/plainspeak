"""
Integration tests for plugin verb matching system.

This module tests the plugin verb matching system across all components:
- Plugin
- PluginRegistry
- PluginManager
- Real plugin implementations
"""

import unittest
from unittest.mock import Mock

from plainspeak.plugins.base import Plugin, PluginRegistry
from plainspeak.plugins.file import FilePlugin
from plainspeak.plugins.network import NetworkPlugin
from plainspeak.plugins.system import SystemPlugin
from plainspeak.plugins.text import TextPlugin


class TestPluginVerbMatchingIntegration(unittest.TestCase):
    """Integration tests for plugin verb matching across components."""

    def setUp(self):
        """Set up test environment."""
        # Create a fresh PluginManager for each test
        from plainspeak.plugins.manager import PluginManager

        self.manager = PluginManager()

        # Override the registry with a test registry
        self.registry = PluginRegistry()
        self.manager.registry = self.registry

        # Register standard plugins
        self.file_plugin = FilePlugin()
        self.text_plugin = TextPlugin()
        self.system_plugin = SystemPlugin()
        self.network_plugin = NetworkPlugin()

        self.registry.register(self.file_plugin)
        self.registry.register(self.text_plugin)
        self.registry.register(self.system_plugin)
        self.registry.register(self.network_plugin)

    def test_plugin_loading(self):
        """Test that plugins are properly loaded."""
        self.assertIn(self.file_plugin, self.registry.plugins.values())
        self.assertIn(self.text_plugin, self.registry.plugins.values())
        self.assertIn(self.system_plugin, self.registry.plugins.values())
        self.assertIn(self.network_plugin, self.registry.plugins.values())

    def test_exact_verb_matching(self):
        """Test exact verb matching with real plugins."""
        # Test file plugin verbs
        plugin = self.manager.get_plugin_for_verb("ls")
        self.assertEqual(plugin, self.file_plugin)

        # Test text plugin verbs
        plugin = self.manager.get_plugin_for_verb("grep")
        self.assertEqual(plugin, self.text_plugin)

    def test_verb_extraction(self):
        """Test that verbs are correctly extracted from natural language."""
        # Test with file operation
        verb, args = self.manager.extract_verb_and_args("ls /tmp")
        self.assertEqual(verb, "ls")
        self.assertEqual(args["path"], "/tmp")

        # Test with text operation
        verb, args = self.manager.extract_verb_and_args("grep error in log.txt")
        self.assertEqual(verb, "grep")
        self.assertIn("pattern", args)
        self.assertEqual(args["pattern"], "error in log.txt")

    def test_verb_conflict_resolution(self):
        """Test that verb conflicts are properly resolved by priority."""
        # Create mock plugins with different priorities
        low_priority = Mock(spec=Plugin)
        low_priority.name = "low"
        low_priority.priority = 1
        low_priority.get_verbs.return_value = ["test"]
        low_priority.get_aliases.return_value = {}

        high_priority = Mock(spec=Plugin)
        high_priority.name = "high"
        high_priority.priority = 100
        high_priority.get_verbs.return_value = ["test"]
        high_priority.get_aliases.return_value = {}

        # Register both plugins
        self.registry.register(low_priority)
        self.registry.register(high_priority)

        # High priority should win
        plugin = self.registry.get_plugin_for_verb("test")
        self.assertEqual(plugin.name, "high")

    def test_caching(self):
        """Test verb lookup caching."""
        # Get verb -> plugin mapping
        verbs = self.manager.get_all_verbs()

        # Verify file plugin verbs are present
        self.assertIn("ls", verbs)
        self.assertEqual(verbs["ls"], self.file_plugin.name)

        # Reload plugins to invalidate cache
        self.manager.reload_plugins()

        # Get updated verb mapping
        new_verbs = self.manager.get_all_verbs()

        # Verify the verb mapping is updated
        self.assertNotEqual(id(verbs), id(new_verbs))


class TestYAMLPluginVerbMatching(unittest.TestCase):
    """Test verb matching with YAML-based plugins."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a plugin manager with test directory
        import os
        import sys

        from plainspeak.plugins.manager import PluginManager

        # Get test plugins directory
        test_plugins_dir = os.path.join(os.path.dirname(__file__), "test_plugins")

        # Add test plugins directory to Python path
        if test_plugins_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(test_plugins_dir))

        # Create plugin manager with test directory
        self.manager = PluginManager()
        self.manager.add_plugin_directory(test_plugins_dir)

        # Force a reload of plugins
        self.manager.reload_plugins()

        # Verify the plugin was loaded
        plugins = self.manager.get_all_plugins()
        if "test_yaml_plugin" not in plugins:
            raise RuntimeError(
                f"Test YAML plugin not loaded. Available plugins: {list(plugins.keys())}\n"
                f"Test plugins directory: {test_plugins_dir}"
            )

    def test_yaml_plugin_matching(self):
        """Test that YAML plugin verbs are matched correctly."""
        verbs = self.manager.get_all_verbs()

        # Test exact matches
        self.assertIn("testverb", verbs)
        self.assertIn("customverb", verbs)

        # Test alias matches
        plugin = self.manager.get_plugin_for_verb("tv")  # alias for testverb
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_yaml_plugin")

        plugin = self.manager.get_plugin_for_verb("cv")  # alias for customverb
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_yaml_plugin")

    def test_yaml_plugin_fuzzy_matching(self):
        """Test fuzzy matching with YAML plugin verbs."""
        # Test with slight misspelling
        plugin = self.manager.get_plugin_for_verb("testvrb")  # missing 'e'
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_yaml_plugin")

        # Test with case difference
        plugin = self.manager.get_plugin_for_verb("TESTVERB")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "test_yaml_plugin")

    def test_yaml_plugin_verbs(self):
        """Test that YAML plugin verbs are available."""
        verbs = self.manager.get_all_verbs()

        # Test main verbs
        self.assertIn("testverb", verbs)
        self.assertIn("customverb", verbs)

        # Test generated commands
        success, command = self.manager.generate_command("testverb", {"option": "value"})
        self.assertTrue(success)
        self.assertEqual(command, "test-command value")

        success, command = self.manager.generate_command("customverb", {"param": "test"})
        self.assertTrue(success)
        self.assertEqual(command, "custom-command test")


if __name__ == "__main__":
    unittest.main()
