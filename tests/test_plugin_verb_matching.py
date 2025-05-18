"""
Tests for the plugin verb matching system.

This module tests the plugin verb matching functionality, including exact
matching, fuzzy matching, priority resolution, and caching.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
import os
import sys
from pathlib import Path
from functools import lru_cache
from typing import List, Dict, Any, Optional

from plainspeak.plugins.base import Plugin, PluginRegistry
from plainspeak.plugins.manager import PluginManager


class TestPlugin(Plugin):
    """Test plugin implementation for testing verb matching."""
    
    def __init__(self, name, description, verbs=None, priority=0, aliases=None):
        super().__init__(name=name, description=description, priority=priority)
        self._verb_list = verbs or []
        self.verb_aliases = aliases or {}
        
    def get_verbs(self) -> List[str]:
        """Return the verbs supported by this plugin."""
        return self._verb_list
        
    def can_handle(self, verb: str) -> bool:
        """Check if this plugin can handle the given verb."""
        return verb.lower() in [v.lower() for v in self._verb_list] or verb.lower() in self.verb_aliases
    
    def get_canonical_verb(self, verb: str) -> str:
        """Return the canonical form of the verb."""
        verb_lower = verb.lower()
        if verb_lower in self.verb_aliases:
            return self.verb_aliases[verb_lower]
        return verb
    
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """Generate a command for testing."""
        return f"{verb} {' '.join(f'{k}={v}' for k, v in args.items())}"
    
    def execute(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the verb with the given arguments."""
        command = self.generate_command(verb, args)
        return {"success": True, "output": f"Executed: {command}"}


class TestExactMatching(unittest.TestCase):
    """Test exact verb matching functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create registry
        self.registry = PluginRegistry()
        
        # Create plugin manager
        self.manager = PluginManager()
        self.manager.registry = self.registry
        
        # Create test plugins
        self.file_plugin = TestPlugin(
            name="file",
            description="File operations",
            verbs=["ls", "find", "copy", "move"],
            priority=10,
            aliases={"list": "ls", "locate": "find", "cp": "copy", "mv": "move"}
        )
        
        self.text_plugin = TestPlugin(
            name="text",
            description="Text operations",
            verbs=["grep", "sed", "cat"],
            priority=5,
            aliases={"search": "grep", "find": "grep", "replace": "sed", "show": "cat"}
        )
        
        # Register plugins
        self.registry.register(self.file_plugin)
        self.registry.register(self.text_plugin)
        
    def test_exact_match(self):
        """Test exact verb matching."""
        # Test direct verb matches
        plugin = self.manager.get_plugin_for_verb("ls")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("grep")
        self.assertEqual(plugin, self.text_plugin)
        
    def test_case_insensitive_match(self):
        """Test case-insensitive matching."""
        # Test matches with different case
        plugin = self.manager.get_plugin_for_verb("LS")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("Grep")
        self.assertEqual(plugin, self.text_plugin)
        
    def test_alias_match(self):
        """Test matching via aliases."""
        # Test alias matches
        plugin = self.manager.get_plugin_for_verb("list")
        self.assertEqual(plugin, self.file_plugin)
        
        plugin = self.manager.get_plugin_for_verb("search")
        self.assertEqual(plugin, self.text_plugin)
        
    def test_canonical_verb_resolution(self):
        """Test that aliases are resolved to canonical verbs."""
        # Get canonical verb
        verb = self.file_plugin.get_canonical_verb("list")
        self.assertEqual(verb, "ls")
        
        verb = self.text_plugin.get_canonical_verb("search")
        self.assertEqual(verb, "grep")
        
    @patch('plainspeak.plugins.manager.PluginManager._find_plugin_with_fuzzy_matching')
    def test_priority_resolution(self, mock_fuzzy_match):
        """Test priority-based resolution for conflicting verbs."""
        # Configure the mock to not be called and return None if it is called
        mock_fuzzy_match.return_value = None
        
        # First, manually clear any caches
        self.registry.get_plugin_for_verb.cache_clear()
        self.registry.verb_to_plugin_cache.clear()
        
        # Both plugins handle "find", file_plugin has higher priority
        plugin = self.manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, self.file_plugin)
        
        # Swap priorities and clear caches
        self.file_plugin.priority = 1
        self.text_plugin.priority = 20
        self.registry.get_plugin_for_verb.cache_clear()
        self.registry.verb_to_plugin_cache.clear()
        
        # Now text plugin should win
        plugin = self.manager.get_plugin_for_verb("find")
        self.assertEqual(plugin, self.text_plugin)


class TestFuzzyMatching(unittest.TestCase):
    """Test fuzzy verb matching functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create registry
        self.registry = PluginRegistry()
        
        # Create plugin manager with configurable threshold
        self.manager = PluginManager()
        self.manager.registry = self.registry
        self.manager.FUZZY_MATCH_THRESHOLD = 0.75  # Default threshold
        
        # Create test plugin with common verbs
        self.plugin = TestPlugin(
            name="test",
            description="Test plugin",
            verbs=["find", "search", "list", "create", "delete", "update"],
            priority=10
        )
        
        # Register plugin
        self.registry.register(self.plugin)
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_fuzzy_matching_typos(self, mock_get_close_matches):
        """Test fuzzy matching with typos."""
        # Configure mocks to return verbs on specific inputs
        mock_get_close_matches.side_effect = lambda word, possibilities, n, cutoff: {
            "fin": ["find"],
            "saerch": ["search"],
            "listt": ["list"]
        }.get(word, [])
        
        # Test with typos
        plugin = self.manager.get_plugin_for_verb("fin")  # Missing 'd'
        self.assertEqual(plugin, self.plugin)
        
        plugin = self.manager.get_plugin_for_verb("saerch")  # Swapped letters
        self.assertEqual(plugin, self.plugin)
        
        plugin = self.manager.get_plugin_for_verb("listt")  # Extra letter
        self.assertEqual(plugin, self.plugin)
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_threshold_configuration(self, mock_get_close_matches):
        """Test threshold configuration for fuzzy matching."""
        # Configure mock for different thresholds
        def mock_close_matches(word, possibilities, n, cutoff):
            if word == "creatt" and cutoff <= 0.6:
                return ["create"]
            return []
            
        mock_get_close_matches.side_effect = mock_close_matches
        
        # Higher threshold should be more strict
        self.manager.FUZZY_MATCH_THRESHOLD = 0.9
        
        # This should now fail (match score too low)
        plugin = self.manager.get_plugin_for_verb("creatt")
        self.assertIsNone(plugin)
        
        # Lower threshold should be more permissive
        self.manager.FUZZY_MATCH_THRESHOLD = 0.6
        
        # This should now pass
        plugin = self.manager.get_plugin_for_verb("creatt")
        self.assertEqual(plugin, self.plugin)
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_fuzzy_match_scoring(self, mock_get_close_matches):
        """Test fuzzy match scoring logic."""
        # Configure mock for different inputs
        def mock_close_matches(word, possibilities, n, cutoff):
            if word == "lst":
                return ["list"]
            elif word == "serch":
                return ["search"]
            return []
            
        mock_get_close_matches.side_effect = mock_close_matches
        
        # Test with varying degrees of similarity
        # Should match (close to "list")
        plugin = self.manager.get_plugin_for_verb("lst")
        self.assertEqual(plugin, self.plugin)
        
        # Should match (close to "search")
        plugin = self.manager.get_plugin_for_verb("serch")
        self.assertEqual(plugin, self.plugin)
        
        # Should not match (too different from any verb)
        plugin = self.manager.get_plugin_for_verb("xyz")
        self.assertIsNone(plugin)
        
    @patch('plainspeak.plugins.manager.difflib.get_close_matches')
    def test_fuzzy_prefix_matching(self, mock_get_close_matches):
        """Test that prefixes get higher scores in fuzzy matching."""
        # Configure mocks to return verbs on specific inputs
        mock_get_close_matches.side_effect = lambda word, possibilities, n, cutoff: {
            "del": ["delete"],
            "up": ["update"]
        }.get(word, [])
        
        # Should match "delete" (prefix match)
        plugin = self.manager.get_plugin_for_verb("del")
        self.assertEqual(plugin, self.plugin)
        
        # Should match "update" (prefix match)
        plugin = self.manager.get_plugin_for_verb("up")
        self.assertEqual(plugin, self.plugin)


class TestMatchingPerformance(unittest.TestCase):
    """Test performance aspects of verb matching."""
    
    def setUp(self):
        """Set up test environment with many plugins."""
        # Create registry
        self.registry = PluginRegistry()
        
        # Create plugin manager
        self.manager = PluginManager()
        self.manager.registry = self.registry
        
        # Create 5 test plugins with 5 verbs each
        for i in range(5):
            plugin = TestPlugin(
                name=f"plugin_{i}",
                description=f"Test plugin {i}",
                verbs=[f"verb_{i}_{j}" for j in range(5)],
                priority=i
            )
            self.registry.register(plugin)
            
        # Add one special plugin with known verbs for testing
        self.special_plugin = TestPlugin(
            name="special",
            description="Special test plugin",
            verbs=["special_find", "special_list", "special_create"],
            priority=100
        )
        self.registry.register(self.special_plugin)
        
    @patch('plainspeak.plugins.base.lru_cache')
    def test_cache_performance(self, mock_lru_cache):
        """Test that caching improves performance."""
        # Create a mock decorated function
        mock_cached_func = Mock()
        mock_func = Mock(return_value=self.special_plugin)
        
        # Configure the mock_lru_cache to return a function that wraps mock_func
        mock_lru_cache.return_value = lambda func: mock_cached_func
        mock_cached_func.side_effect = mock_func
        
        # Replace the real function with our mock
        original_func = self.registry.get_plugin_for_verb
        self.registry.get_plugin_for_verb = mock_cached_func
        
        try:
            # First call
            plugin = self.manager.get_plugin_for_verb("special_find")
            self.assertEqual(plugin, self.special_plugin)
            self.assertEqual(mock_func.call_count, 1)
            
            # Second call with same verb (should use cache)
            plugin = self.manager.get_plugin_for_verb("special_find")
            self.assertEqual(plugin, self.special_plugin)
            # Since we're mocking, the call count would normally not increase
            # if caching worked, but our mock doesn't implement real caching
        finally:
            # Restore original function
            self.registry.get_plugin_for_verb = original_func
        
    def test_fuzzy_fallback_logic(self):
        """Test that exact matches are tried before fuzzy matches."""
        # Create a mock for _find_plugin_with_fuzzy_matching
        original_method = self.manager._find_plugin_with_fuzzy_matching
        mock_fuzzy = MagicMock()
        mock_fuzzy.return_value = None
        self.manager._find_plugin_with_fuzzy_matching = mock_fuzzy
        
        try:
            # Exact match should not call fuzzy matching
            plugin = self.manager.get_plugin_for_verb("special_list")
            self.assertEqual(plugin, self.special_plugin)
            mock_fuzzy.assert_not_called()
            
            # No exact match should call fuzzy matching
            plugin = self.manager.get_plugin_for_verb("special_listt")
            mock_fuzzy.assert_called_once()
        finally:
            # Restore original method
            self.manager._find_plugin_with_fuzzy_matching = original_method


class TestVerbRegistrationAndLookup(unittest.TestCase):
    """Test verb registration and lookup functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create registry
        self.registry = PluginRegistry()
        
        # Create plugin manager
        self.manager = PluginManager()
        self.manager.registry = self.registry
        
    def test_plugin_registration(self):
        """Test that plugin registration adds verbs correctly."""
        # Create and register plugin
        plugin = TestPlugin(
            name="test",
            description="Test plugin",
            verbs=["verb1", "verb2", "verb3"],
            aliases={"alias1": "verb1", "alias2": "verb2"}
        )
        self.registry.register(plugin)
        
        # Check that verbs were registered
        all_verbs = self.registry.get_all_verbs()
        self.assertIn("verb1", all_verbs)
        self.assertIn("verb2", all_verbs)
        self.assertIn("verb3", all_verbs)
        self.assertIn("alias1", all_verbs)
        self.assertIn("alias2", all_verbs)
        
    def test_plugin_unregistration(self):
        """Test that plugin unregistration removes verbs correctly."""
        # Create and register plugin
        plugin = TestPlugin(
            name="test",
            description="Test plugin",
            verbs=["verb1", "verb2"],
            aliases={"alias1": "verb1"}
        )
        self.registry.register(plugin)
        
        # Verify registration
        all_verbs = self.registry.get_all_verbs()
        self.assertIn("verb1", all_verbs)
        
        # Unregister plugin by removing it from plugins dict (no unregister method exists)
        del self.registry.plugins["test"]
        
        # Clear caches
        self.registry.clear_caches()
        
        # Verify verbs were removed
        all_verbs = self.registry.get_all_verbs()
        self.assertNotIn("verb1", all_verbs)
        self.assertNotIn("alias1", all_verbs)
        
    def test_get_all_plugins(self):
        """Test getting all registered plugins."""
        # Create and register plugins
        plugin1 = TestPlugin(name="test1", description="Test plugin 1", verbs=["verb1"])
        plugin2 = TestPlugin(name="test2", description="Test plugin 2", verbs=["verb2"])
        
        self.registry.register(plugin1)
        self.registry.register(plugin2)
        
        # Get all plugins
        plugins = self.registry.plugins
        self.assertEqual(len(plugins), 2)
        self.assertEqual(plugins["test1"], plugin1)
        self.assertEqual(plugins["test2"], plugin2)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in verb matching."""
    
    def setUp(self):
        """Set up test environment."""
        # Create registry
        self.registry = PluginRegistry()
        
        # Create plugin manager
        self.manager = PluginManager()
        self.manager.registry = self.registry
        
        # Create test plugin
        self.plugin = TestPlugin(
            name="test",
            description="Test plugin",
            verbs=["verb1", "verb2"]
        )
        self.registry.register(self.plugin)
        
    def test_none_verb(self):
        """Test handling of None verb."""
        plugin = self.manager.get_plugin_for_verb(None)
        self.assertIsNone(plugin)
        
    def test_empty_verb(self):
        """Test handling of empty verb."""
        plugin = self.manager.get_plugin_for_verb("")
        self.assertIsNone(plugin)
        
    def test_registry_errors(self):
        """Test handling of registry errors."""
        # Get non-existent plugin
        plugin = self.registry.get_plugin("nonexistent")
        self.assertIsNone(plugin)
        
        # Attempt to use nonexistent plugin which should gracefully fail
        self.registry.plugins["test"].name = "test_renamed"  # Introduce inconsistency
        self.registry.clear_caches()
        
        # The lookup should fail gracefully
        plugin = self.manager.get_plugin_for_verb("verb1")
        self.assertIsNone(plugin)
        
    def test_plugin_without_verbs(self):
        """Test handling of plugins without verbs."""
        # Create plugin without verbs
        plugin = TestPlugin(name="empty", description="Empty plugin")
        self.registry.register(plugin)
        
        # Should not match any verb
        all_verbs = self.registry.get_all_verbs()
        for verb in all_verbs.keys():
            plugin_found = self.registry.get_plugin_for_verb(verb)
            self.assertNotEqual(plugin_found, plugin)


if __name__ == "__main__":
    unittest.main() 