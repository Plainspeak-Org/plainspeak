"""
Integration tests for plugin verb matching system.

This module tests the plugin verb matching system across all components:
- Plugin
- PluginRegistry
- PluginManager
- Real plugin implementations

These tests ensure the verb matching system works correctly in a real-world scenario.
"""

import unittest
from unittest.mock import patch, Mock
import os
import tempfile
from pathlib import Path

from plainspeak.plugins.base import Plugin, PluginRegistry
from plainspeak.plugins.manager import PluginManager
from plainspeak.plugins.file import FilePlugin
from plainspeak.plugins.text import TextPlugin
from plainspeak.plugins.system import SystemPlugin
from plainspeak.plugins.network import NetworkPlugin


class TestPluginVerbMatchingIntegration(unittest.TestCase):
    """Integration tests for plugin verb matching across components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a fresh PluginManager for each test
        self.manager = PluginManager()
        
        # Override the registry with a test registry to control test conditions
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
        plugins = self.manager.get_all_plugins()
        self.assertIn("file", plugins)
        self.assertIn("text", plugins)
        self.assertIn("system", plugins)
        self.assertIn("network", plugins)
        
        # Test that plugin verbs are available
        verbs = self.manager.get_all_verbs()
        
        # File plugin verbs
        self.assertIn("ls", verbs)
        self.assertIn("find", verbs)
        self.assertIn("copy", verbs)
        
        # Text plugin verbs
        self.assertIn("grep", verbs)
        self.assertIn("sed", verbs)
        
        # System plugin verbs
        self.assertIn("ps", verbs)
        self.assertIn("top", verbs)
        
        # Network plugin verbs
        self.assertIn("ping", verbs)
        self.assertIn("wget", verbs)
        
    def test_exact_verb_matching(self):
        """Test exact verb matching with real plugins."""
        # Test file plugin verbs
        plugin = self.manager.get_plugin_for_verb("ls")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, self.file_plugin)
        
        # Test text plugin verbs
        plugin = self.manager.get_plugin_for_verb("grep")
        self.assertEqual(plugin, self.text_plugin)
        
        # Test system plugin verbs
        plugin = self.manager.get_plugin_for_verb("ps")
        self.assertEqual(plugin, self.system_plugin)
        
        # Test network plugin verbs
        plugin = self.manager.get_plugin_for_verb("ping")
        self.assertEqual(plugin, self.network_plugin)
        
    def test_case_insensitive_matching(self):
        """Test that verb matching is case-insensitive."""
        plugin = self.manager.get_plugin_for_verb("LS")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("Grep")
        self.assertEqual(plugin, self.text_plugin)
        
        plugin = self.manager.get_plugin_for_verb("PS")
        self.assertEqual(plugin, self.system_plugin)
        
    def test_fuzzy_matching(self):
        """Test fuzzy matching with real plugins."""
        # Test typos in verbs
        plugin = self.manager.get_plugin_for_verb("fin")  # "find" with missing "d"
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("cop")  # "copy" with missing "y"
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("grpe")  # "grep" with transposed letters
        self.assertEqual(plugin, self.text_plugin)
        
    def test_verb_conflict_resolution(self):
        """Test that verb conflicts are properly resolved by priority."""
        # Create a high-priority plugin that handles a common verb
        high_priority_plugin = Mock(spec=Plugin)
        high_priority_plugin.name = "high_priority"
        high_priority_plugin.priority = 100
        high_priority_plugin.get_verbs.return_value = ["find"]  # Same as file plugin
        high_priority_plugin.get_aliases.return_value = {}
        high_priority_plugin.can_handle.return_value = True
        
        # Register the high-priority plugin
        self.registry.register(high_priority_plugin)
        
        # The high-priority plugin should handle the verb
        plugin = self.manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, high_priority_plugin)
        
        # Create another plugin with even higher priority
        highest_priority_plugin = Mock(spec=Plugin)
        highest_priority_plugin.name = "highest_priority"
        highest_priority_plugin.priority = 200
        highest_priority_plugin.get_verbs.return_value = ["find"]
        highest_priority_plugin.get_aliases.return_value = {}
        highest_priority_plugin.can_handle.return_value = True
        
        # Register the highest-priority plugin
        self.registry.register(highest_priority_plugin)
        
        # The highest-priority plugin should now handle the verb
        plugin = self.manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, highest_priority_plugin)
        
    def test_verb_aliases(self):
        """Test that verb aliases work correctly."""
        # The FilePlugin aliases "ls" as "list" and "dir"
        plugin = self.manager.get_plugin_for_verb("list")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("dir")
        self.assertEqual(plugin, self.file_plugin)
        
        # The TextPlugin aliases "grep" as "search" and "find-text"
        plugin = self.manager.get_plugin_for_verb("search")
        self.assertEqual(plugin, self.text_plugin)
        
    def test_command_generation(self):
        """Test that commands are correctly generated for matched verbs."""
        # Test file plugin command generation
        success, command = self.manager.generate_command("ls", {"path": "/tmp"})
        self.assertTrue(success)
        self.assertIn("ls", command)
        self.assertIn("/tmp", command)
        
        # Test text plugin command generation
        success, command = self.manager.generate_command("grep", {"pattern": "error", "file": "log.txt"})
        self.assertTrue(success)
        self.assertIn("grep", command)
        self.assertIn("error", command)
        self.assertIn("log.txt", command)
        
    def test_verb_extraction(self):
        """Test that verbs are correctly extracted from natural language."""
        # Test simple verb extraction
        verb, args = self.manager.extract_verb_and_args("ls /tmp")
        self.assertEqual(verb, "ls")
        self.assertIn("path", args)
        self.assertEqual(args["path"], "/tmp")
        
        # Test more complex verb extraction
        verb, args = self.manager.extract_verb_and_args("grep error in log.txt")
        self.assertEqual(verb, "grep")
        self.assertIn("text", args)
        self.assertEqual(args["text"], "error in log.txt")
        
    def test_caching(self):
        """Test that verb lookup caching works properly."""
        # First call should miss cache
        plugin1 = self.manager.get_plugin_for_verb("ls")
        self.assertEqual(plugin1, self.file_plugin)
        
        # Create a new plugin with higher priority for the same verb
        high_priority_plugin = Mock(spec=Plugin)
        high_priority_plugin.name = "high_priority"
        high_priority_plugin.priority = 100
        high_priority_plugin.get_verbs.return_value = ["ls"]
        high_priority_plugin.get_aliases.return_value = {}
        high_priority_plugin.can_handle.return_value = True
        
        # Register the high-priority plugin
        self.registry.register(high_priority_plugin)
        
        # Cache should be invalidated, and high-priority plugin should be returned
        plugin2 = self.manager.get_plugin_for_verb("ls")
        self.assertEqual(plugin2, high_priority_plugin)
        
    def test_error_handling(self):
        """Test that error cases are properly handled."""
        # Test with unknown verb
        plugin = self.manager.get_plugin_for_verb("unknown_verb")
        self.assertIsNone(plugin)
        
        # Test with empty verb
        plugin = self.manager.get_plugin_for_verb("")
        self.assertIsNone(plugin)
        
        # Test error in command generation
        self.file_plugin.generate_command = Mock(side_effect=Exception("Test error"))
        success, error = self.manager.generate_command("ls", {})
        self.assertFalse(success)
        self.assertIn("Error generating command", error)


class TestYAMLPluginVerbMatching(unittest.TestCase):
    """Test verb matching with YAML plugins."""
    
    def setUp(self):
        """Set up a temporary YAML plugin."""
        # Create a temporary directory for plugin
        self.temp_dir = tempfile.TemporaryDirectory()
        self.plugin_dir = Path(self.temp_dir.name)
        
        # Create a YAML manifest
        manifest_path = self.plugin_dir / "manifest.yaml"
        
        with open(manifest_path, "w") as f:
            f.write("""
name: yaml_plugin
description: A test YAML plugin
priority: 10
verbs:
  - custom_verb
  - another_verb
verb_aliases:
  custom_verb:
    - cv
    - customverb
  another_verb:
    - av
commands:
  custom_verb:
    template: "custom-command {{ option }}"
    description: "A custom command"
  another_verb:
    template: "another-command {{ param }}"
    description: "Another command"
entrypoint: plainspeak.plugins.test_plugin.TestPlugin
            """)
        
        # Setup test plugin class
        self.plugin_module_path = self.plugin_dir / "test_plugin.py"
        with open(self.plugin_module_path, "w") as f:
            f.write("""
from plainspeak.plugins.base import YAMLPlugin
from pathlib import Path

class TestPlugin(YAMLPlugin):
    def __init__(self):
        super().__init__(Path(__file__).parent / "manifest.yaml")
            """)
        
        # Add plugin directory to path
        import sys
        sys.path.append(str(self.plugin_dir))
        
        # Create plugin manager with plugin directory
        self.manager = PluginManager()
        self.manager.add_plugin_directory(str(self.plugin_dir))
        
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
        
    def test_yaml_plugin_loading(self):
        """Test that YAML plugin is loaded correctly."""
        plugins = self.manager.get_all_plugins()
        self.assertIn("yaml_plugin", plugins)
        
    def test_yaml_plugin_verbs(self):
        """Test that YAML plugin verbs are available."""
        verbs = self.manager.get_all_verbs()
        self.assertIn("custom_verb", verbs)
        self.assertIn("another_verb", verbs)
        self.assertIn("cv", verbs)  # Alias
        self.assertIn("customverb", verbs)  # Alias
        self.assertIn("av", verbs)  # Alias
        
    def test_yaml_plugin_matching(self):
        """Test that YAML plugin verbs are matched correctly."""
        plugin = self.manager.get_plugin_for_verb("custom_verb")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "yaml_plugin")
        
        # Test alias matching
        plugin = self.manager.get_plugin_for_verb("cv")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "yaml_plugin")
        
        plugin = self.manager.get_plugin_for_verb("customverb")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "yaml_plugin")
        
    def test_yaml_plugin_fuzzy_matching(self):
        """Test fuzzy matching with YAML plugin verbs."""
        # Test typo in verb
        plugin = self.manager.get_plugin_for_verb("custm_verb")  # Missing "o"
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "yaml_plugin")
        
        # Test typo in alias
        plugin = self.manager.get_plugin_for_verb("custmverb")  # Missing "o"
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "yaml_plugin")


if __name__ == "__main__":
    unittest.main() 