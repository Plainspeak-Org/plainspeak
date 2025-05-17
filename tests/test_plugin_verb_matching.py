"""
Unit tests for plugin verb matching system.

This module tests the enhanced plugin verb matching system, including:
- Exact matching
- Fuzzy matching
- Priority-based resolution
- Verb aliases
"""

import unittest
from unittest.mock import Mock, patch
import tempfile
import os
from pathlib import Path

from plainspeak.plugins.base import Plugin, PluginRegistry
from plainspeak.plugins.manager import PluginManager
from plainspeak.plugins.schemas import PluginManifest, CommandConfig


class TestPlugin(Plugin):
    """Test plugin implementation for tests."""
    
    def __init__(self, name, description, verbs, priority=0, aliases=None):
        super().__init__(name, description, priority)
        self._verbs = verbs
        if aliases:
            self.verb_aliases = aliases
            
    def get_verbs(self):
        return self._verbs
        
    def generate_command(self, verb, args):
        return f"Command for {verb} with args {args}"


class TestExactMatching(unittest.TestCase):
    """Test exact matching of verbs to plugins."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        self.plugin1 = TestPlugin("plugin1", "Test Plugin 1", ["find", "search"], 10)
        self.plugin2 = TestPlugin("plugin2", "Test Plugin 2", ["list", "show"], 5)
        self.registry.register(self.plugin1)
        self.registry.register(self.plugin2)
        
    def test_exact_match(self):
        """Test exact matching of verbs."""
        plugin = self.registry.get_plugin_for_verb("find")
        self.assertEqual(plugin, self.plugin1)
        
        plugin = self.registry.get_plugin_for_verb("list")
        self.assertEqual(plugin, self.plugin2)
        
    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        plugin = self.registry.get_plugin_for_verb("Find")
        self.assertEqual(plugin, self.plugin1)
        
        plugin = self.registry.get_plugin_for_verb("LIST")
        self.assertEqual(plugin, self.plugin2)
        
    def test_no_match(self):
        """Test no match is found for unknown verbs."""
        plugin = self.registry.get_plugin_for_verb("unknown")
        self.assertIsNone(plugin)
        
    def test_empty_verb(self):
        """Test empty verb returns None."""
        plugin = self.registry.get_plugin_for_verb("")
        self.assertIsNone(plugin)


class TestPriorityResolution(unittest.TestCase):
    """Test priority-based resolution of plugins."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        self.plugin1 = TestPlugin("plugin1", "Test Plugin 1", ["find"], 10)
        self.plugin2 = TestPlugin("plugin2", "Test Plugin 2", ["find"], 20)  # Higher priority
        self.plugin3 = TestPlugin("plugin3", "Test Plugin 3", ["find"], 5)
        self.registry.register(self.plugin1)
        self.registry.register(self.plugin2)
        self.registry.register(self.plugin3)
        
    def test_priority_resolution(self):
        """Test that higher priority plugins are returned first."""
        plugin = self.registry.get_plugin_for_verb("find")
        # Should return plugin2 as it has the highest priority
        self.assertEqual(plugin, self.plugin2)


class TestVerbAliases(unittest.TestCase):
    """Test verb aliases functionality."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        # Plugin with verb aliases
        self.plugin = TestPlugin(
            "plugin", 
            "Test Plugin", 
            ["find"],
            aliases={"search": "find", "locate": "find"}
        )
        self.registry.register(self.plugin)
        
    def test_alias_matching(self):
        """Test that aliases are correctly matched to plugins."""
        plugin = self.registry.get_plugin_for_verb("search")
        self.assertEqual(plugin, self.plugin)
        
        plugin = self.registry.get_plugin_for_verb("locate")
        self.assertEqual(plugin, self.plugin)
        
    def test_canonical_verb_retrieval(self):
        """Test that canonical verbs can be retrieved from aliases."""
        canonical = self.plugin.get_canonical_verb("search")
        self.assertEqual(canonical, "find")
        
        canonical = self.plugin.get_canonical_verb("locate")
        self.assertEqual(canonical, "find")
        
        # Original verb should return itself
        canonical = self.plugin.get_canonical_verb("find")
        self.assertEqual(canonical, "find")
        
    def test_get_all_verbs(self):
        """Test that get_all_verbs includes aliases."""
        verbs = self.registry.get_all_verbs()
        self.assertIn("find", verbs)
        self.assertIn("search", verbs)
        self.assertIn("locate", verbs)
        self.assertEqual(len(verbs), 3)


class TestFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching of verbs."""
    
    def setUp(self):
        # Setup PluginManager with mocked registry
        self.manager = PluginManager()
        self.manager.registry = PluginRegistry()
        self.plugin = TestPlugin("plugin", "Test Plugin", ["search", "download"])
        self.manager.registry.register(self.plugin)
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_fuzzy_matching(self, mock_get_close_matches):
        """Test fuzzy matching with difflib."""
        # Mock difflib to return a match
        mock_get_close_matches.return_value = ["search"]
        
        # Test typo in verb
        plugin = self.manager.get_plugin_for_verb("serch")
        self.assertEqual(plugin, self.plugin)
        
        # Verify difflib was called correctly
        mock_get_close_matches.assert_called_with(
            "serch", 
            ["search", "download"], 
            n=1, 
            cutoff=PluginManager.FUZZY_MATCH_THRESHOLD
        )
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_fuzzy_matching_no_match(self, mock_get_close_matches):
        """Test fuzzy matching with no close matches."""
        # Mock difflib to return no matches
        mock_get_close_matches.return_value = []
        
        # Test with a verb that's very different
        plugin = self.manager.get_plugin_for_verb("xyz")
        self.assertIsNone(plugin)
        
    @patch('plainspeak.plugins.manager.logger')
    def test_logging(self, mock_logger):
        """Test that logging is performed."""
        # Test with valid verb to check debug logging
        self.manager.get_plugin_for_verb("search")
        mock_logger.debug.assert_called()


class TestCaching(unittest.TestCase):
    """Test caching functionality."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        self.plugin = TestPlugin("plugin", "Test Plugin", ["find"])
        self.registry.register(self.plugin)
        
    def test_lru_cache(self):
        """Test that the LRU cache is working."""
        # Call the method multiple times with the same verb
        for _ in range(5):
            plugin = self.registry.get_plugin_for_verb("find")
            self.assertEqual(plugin, self.plugin)
            
        # Check cache info to confirm caching is working
        cache_info = self.registry.get_plugin_for_verb.cache_info()
        self.assertGreater(cache_info.hits, 0)


if __name__ == '__main__':
    unittest.main() 