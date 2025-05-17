"""
Unit tests for plugin verb matching system.

This module tests the enhanced plugin verb matching system, including:
- Exact matching
- Fuzzy matching
- Priority-based resolution
- Verb aliases
- Performance optimization (LRU caching)
- Error handling and logging
"""

import unittest
from unittest.mock import Mock, patch, call
import tempfile
import os
from pathlib import Path
import time

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
        
    def test_equal_priority_resolution(self):
        """Test that when priorities are equal, plugins registered first take precedence."""
        registry = PluginRegistry()
        plugin1 = TestPlugin("plugin1", "Test Plugin 1", ["duplicate"], 10)
        plugin2 = TestPlugin("plugin2", "Test Plugin 2", ["duplicate"], 10)  # Same priority
        registry.register(plugin1)
        registry.register(plugin2)
        
        plugin = registry.get_plugin_for_verb("duplicate")
        # Should return plugin1 as it was registered first
        self.assertEqual(plugin, plugin1)


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
        
    def test_case_insensitive_alias_matching(self):
        """Test case-insensitive alias matching."""
        plugin = self.registry.get_plugin_for_verb("SeArCh")
        self.assertEqual(plugin, self.plugin)
        
        plugin = self.registry.get_plugin_for_verb("LOCATE")
        self.assertEqual(plugin, self.plugin)
        
    def test_nonexistent_verb_canonical(self):
        """Test that ValueError is raised for non-existent verbs."""
        with self.assertRaises(ValueError):
            self.plugin.get_canonical_verb("nonexistent")


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
        
    def test_real_fuzzy_matching(self):
        """Test real fuzzy matching with actual difflib."""
        # Test with actual fuzzy matching (not mocked)
        plugin = self.manager.get_plugin_for_verb("srch")  # Missing 'ea'
        self.assertEqual(plugin, self.plugin)
        
        plugin = self.manager.get_plugin_for_verb("donload")  # 'w' replaced with 'n'
        self.assertEqual(plugin, self.plugin)
        
        # Test with a verb that's too different
        plugin = self.manager.get_plugin_for_verb("run")
        self.assertIsNone(plugin)


class TestCaching(unittest.TestCase):
    """Test caching functionality."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        self.plugin = TestPlugin("plugin", "Test Plugin", ["find", "search"])
        self.registry.register(self.plugin)
        
    def test_lru_cache(self):
        """Test that LRU cache works correctly."""
        # This test ensures that subsequent calls use the cache
        original_get_plugin_for_verb = self.registry.get_plugin_for_verb
        
        # Create a wrapper to track calls
        call_count = 0
        
        def tracking_get_plugin_for_verb(verb):
            nonlocal call_count
            call_count += 1
            return original_get_plugin_for_verb.__wrapped__(self.registry, verb)
            
        # Replace the method with our tracking version
        self.registry.get_plugin_for_verb = tracking_get_plugin_for_verb
        
        # First call should hit the function
        plugin1 = self.registry.get_plugin_for_verb("find")
        self.assertEqual(plugin1, self.plugin)
        self.assertEqual(call_count, 1)
        
        # Second call with same verb should use cache
        plugin2 = self.registry.get_plugin_for_verb("find")
        self.assertEqual(plugin2, self.plugin)
        self.assertEqual(call_count, 1)  # Still 1 because cache was used
        
        # Different verb should call the function again
        plugin3 = self.registry.get_plugin_for_verb("search")
        self.assertEqual(plugin3, self.plugin)
        self.assertEqual(call_count, 2)
        
    def test_cache_invalidation(self):
        """Test that cache is invalidated when plugins change."""
        manager = PluginManager()
        registry = PluginRegistry()
        plugin1 = TestPlugin("plugin1", "Test Plugin 1", ["find"])
        registry.register(plugin1)
        
        # Mock the registry on the manager
        manager.registry = registry
        
        # First call
        plugin = manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, plugin1)
        
        # Register a new plugin with higher priority for the same verb
        plugin2 = TestPlugin("plugin2", "Test Plugin 2", ["find"], 20)
        registry.register(plugin2)
        
        # Call again, should return the new plugin
        plugin = manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, plugin2)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the verb matching system."""
    
    def setUp(self):
        self.manager = PluginManager()
        
    @patch('plainspeak.plugins.manager.logger')
    def test_generate_command_error(self, mock_logger):
        """Test error handling in generate_command method."""
        registry = PluginRegistry()
        
        # Create a plugin that raises an exception in generate_command
        plugin = TestPlugin("error_plugin", "Error Plugin", ["test"])
        plugin.generate_command = Mock(side_effect=Exception("Test error"))
        
        registry.register(plugin)
        self.manager.registry = registry
        
        # Generate command should return error
        success, message = self.manager.generate_command("test", {})
        self.assertFalse(success)
        self.assertIn("Error generating command", message)
        
        # Logger should have recorded the error
        mock_logger.error.assert_called()
        
    @patch('plainspeak.plugins.manager.logger')
    def test_extract_verb_error(self, mock_logger):
        """Test error handling in extract_verb_and_args method."""
        # Test with None input
        verb, args = self.manager.extract_verb_and_args(None)
        self.assertIsNone(verb)
        self.assertEqual(args, {})
        
        # Test with empty string
        verb, args = self.manager.extract_verb_and_args("")
        self.assertIsNone(verb)
        self.assertEqual(args, {})
        
        # Logger should have recorded warnings
        mock_logger.warning.assert_called()


class TestPerformance(unittest.TestCase):
    """Test performance of the verb matching system."""
    
    def setUp(self):
        self.registry = PluginRegistry()
        # Create 100 plugins with unique verbs
        for i in range(100):
            plugin = TestPlugin(
                f"plugin{i}", 
                f"Test Plugin {i}", 
                [f"verb{i}"], 
                priority=i
            )
            self.registry.register(plugin)
            
        # Create one plugin with 100 verbs
        self.many_verbs_plugin = TestPlugin(
            "many_verbs", 
            "Plugin with many verbs", 
            [f"many_verb{i}" for i in range(100)],
            priority=100
        )
        self.registry.register(self.many_verbs_plugin)
        
    def test_lookup_performance(self):
        """Test lookup performance with many plugins and verbs."""
        # Warm up the cache
        for i in range(100):
            _ = self.registry.get_plugin_for_verb(f"verb{i}")
            
        # Measure time to look up all verbs
        start_time = time.time()
        for i in range(100):
            plugin = self.registry.get_plugin_for_verb(f"verb{i}")
            self.assertIsNotNone(plugin)
            
        # Many plugins lookup should be reasonably fast
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 0.1, "Lookup of 100 verbs took too long")
        
        # Test many verbs in one plugin
        start_time = time.time()
        for i in range(100):
            plugin = self.registry.get_plugin_for_verb(f"many_verb{i}")
            self.assertEqual(plugin, self.many_verbs_plugin)
            
        # Many verbs lookup should be reasonably fast
        elapsed_time = time.time() - start_time
        self.assertLess(elapsed_time, 0.1, "Lookup of 100 verbs in one plugin took too long")


if __name__ == "__main__":
    unittest.main() 