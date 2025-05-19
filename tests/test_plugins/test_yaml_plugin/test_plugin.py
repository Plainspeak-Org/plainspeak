"""Test plugin implementation for YAML plugin tests."""

import os
import unittest

from plainspeak.plugins.base import YAMLPlugin


class YAMLTestPlugin(YAMLPlugin):
    """A test plugin implementation."""

    def __init__(self):
        """Initialize the test plugin."""
        manifest_path = os.path.join(os.path.dirname(__file__), "manifest.yaml")
        super().__init__(manifest_path)


class TestYAMLPlugin(unittest.TestCase):
    """Test cases for YAML plugin."""

    def setUp(self):
        """Set up test environment."""
        self.plugin = YAMLTestPlugin()

    def test_plugin_initialization(self):
        """Test that plugin initializes correctly."""
        self.assertEqual(self.plugin.name, "test_yaml_plugin")
        self.assertEqual(self.plugin.priority, 10)

    def test_plugin_verbs(self):
        """Test that verbs are loaded correctly."""
        verbs = self.plugin.get_verbs()
        self.assertIn("testverb", verbs)
        self.assertIn("customverb", verbs)

    def test_plugin_verb_aliases(self):
        """Test that verb aliases are loaded correctly."""
        aliases = self.plugin.get_aliases()
        self.assertIn("tv", aliases)
        self.assertIn("cv", aliases)
        self.assertEqual(aliases["tv"], "testverb")
        self.assertEqual(aliases["cv"], "customverb")
