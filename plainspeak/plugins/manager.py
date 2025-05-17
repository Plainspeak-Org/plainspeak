"""
Plugin Manager for PlainSpeak.

This module provides a manager for loading and using plugins.
"""
from typing import Dict, List, Any, Optional, Tuple, Iterator
import re
from pathlib import Path
import importlib
import importlib.metadata
import importlib.util
from importlib.metadata import EntryPoint
import sys
import logging
from functools import lru_cache

from .base import Plugin, registry, YAMLPlugin
from .schemas import PluginManifest, EntryPointConfig, PluginConfig

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manager for PlainSpeak plugins.
    
    This class provides methods for:
    - Loading plugins from entry points
    - Finding plugins for verbs
    - Generating commands using plugins
    - Managing plugin lifecycle and dependencies
    """
    
    ENTRY_POINT_GROUP = "plainspeak.plugins"
    
    def __init__(self):
        """Initialize the plugin manager."""
        self.registry = registry
        self.configs: Dict[str, PluginConfig] = {}
        
    def load_plugins(self) -> None:
        """
        Load all available plugins from entry points.
        
        This method:
        1. Discovers plugins via entry points
        2. Loads their manifests
        3. Validates dependencies
        4. Instantiates plugin classes
        5. Registers working plugins
        """
        for entry_point in self._discover_plugins():
            try:
                # Load the entry point configuration
                config = self._load_entry_point(entry_point)
                if not config:
                    continue
                    
                # Load and validate the manifest
                manifest = self._load_manifest(config.manifest_path)
                if not manifest:
                    continue
                    
                # Create plugin config
                plugin_config = PluginConfig(manifest=manifest)
                self.configs[manifest.name] = plugin_config
                
                # Check dependencies
                if not self._check_dependencies(manifest):
                    plugin_config.load_error = "Missing dependencies"
                    continue
                    
                # Load the plugin class
                plugin_class = self._load_plugin_class(config.class_path)
                if not plugin_class:
                    continue
                    
                # Instantiate and register the plugin
                try:
                    plugin = plugin_class()
                    plugin_config.instance = plugin
                    self.registry.register(plugin)
                    logger.info(f"Successfully loaded plugin: {manifest.name}")
                except Exception as e:
                    plugin_config.load_error = f"Failed to instantiate: {e}"
                    logger.error(f"Failed to load plugin {manifest.name}: {e}")
                    
            except Exception as e:
                logger.error(f"Error loading plugin from {entry_point}: {e}")
                
    @lru_cache(maxsize=None)
    def _discover_plugins(self) -> Iterator[EntryPoint]:
        """
        Discover plugins via entry points.
        
        Returns:
            Iterator of entry points in the plainspeak.plugins group.
        """
        try:
            return importlib.metadata.entry_points().get(self.ENTRY_POINT_GROUP, [])
        except Exception as e:
            logger.error(f"Error discovering plugins: {e}")
            return iter([])
            
    def _load_entry_point(self, entry_point: EntryPoint) -> Optional[EntryPointConfig]:
        """
        Load configuration from an entry point.
        
        Args:
            entry_point: The entry point to load.
            
        Returns:
            EntryPointConfig if successful, None if failed.
        """
        try:
            config_func = entry_point.load()
            return EntryPointConfig.parse_obj(config_func())
        except Exception as e:
            logger.error(f"Failed to load entry point {entry_point.name}: {e}")
            return None
            
    def _load_manifest(self, manifest_path: str) -> Optional[PluginManifest]:
        """
        Load and validate a plugin manifest.
        
        Args:
            manifest_path: Path to the manifest file.
            
        Returns:
            PluginManifest if valid, None if invalid.
        """
        try:
            if manifest_path.endswith('.yaml') or manifest_path.endswith('.yml'):
                return YAMLPlugin(Path(manifest_path)).manifest
            else:
                logger.error(f"Unsupported manifest format: {manifest_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            return None
            
    def _check_dependencies(self, manifest: PluginManifest) -> bool:
        """
        Check if all plugin dependencies are satisfied.
        
        Args:
            manifest: The plugin manifest to check.
            
        Returns:
            True if all dependencies are met, False otherwise.
        """
        for package, version in manifest.dependencies.items():
            try:
                pkg_version = importlib.metadata.version(package)
                # TODO: Add proper version comparison
                if not pkg_version:
                    logger.error(f"Missing dependency {package}>={version}")
                    return False
            except importlib.metadata.PackageNotFoundError:
                logger.error(f"Missing dependency {package}>={version}")
                return False
        return True
        
    def _load_plugin_class(self, class_path: str) -> Optional[type]:
        """
        Load a plugin class by import path.
        
        Args:
            class_path: Full import path to the plugin class.
            
        Returns:
            The plugin class if found, None otherwise.
        """
        try:
            module_path, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except Exception as e:
            logger.error(f"Failed to load plugin class {class_path}: {e}")
            return None
        
    def get_all_plugins(self) -> Dict[str, PluginConfig]:
        """
        Get all plugin configurations.
        
        Returns:
            Dictionary of plugin names to configurations.
        """
        return self.configs
        
    def get_all_verbs(self) -> Dict[str, str]:
        """
        Get all verbs from all plugins.
        
        Returns:
            Dictionary mapping verb to plugin name.
        """
        return self.registry.get_all_verbs()
        
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        """
        Get the plugin that can handle the given verb.
        
        Args:
            verb: The verb to handle.
            
        Returns:
            The plugin that can handle the verb, or None if not found.
        """
        return self.registry.get_plugin_for_verb(verb)
        
    def generate_command(self, verb: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Generate a command for the given verb and arguments.
        
        Args:
            verb: The verb to handle.
            args: Arguments for the verb.
            
        Returns:
            Tuple of (success, command or error message).
        """
        plugin = self.get_plugin_for_verb(verb)
        if not plugin:
            return False, f"No plugin found for verb: {verb}"
            
        try:
            command = plugin.generate_command(verb, args)
            return True, command
        except Exception as e:
            return False, f"Error generating command: {e}"
            
    def extract_verb_and_args(self, natural_text: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract the verb and arguments from natural text.
        
        This is a simple implementation that looks for known verbs at the beginning
        of the text. A more sophisticated implementation would use NLP techniques.
        
        Args:
            natural_text: The natural language text.
            
        Returns:
            Tuple of (verb, arguments dictionary).
        """
        # Get all verbs
        all_verbs = self.get_all_verbs()
        
        # Convert to lowercase for case-insensitive matching
        text_lower = natural_text.lower()
        
        # Try to find a verb at the beginning of the text
        for verb in all_verbs.keys():
            # Check if the text starts with the verb
            if text_lower.startswith(verb.lower()):
                # Extract the rest of the text as arguments
                args_text = natural_text[len(verb):].strip()
                
                # Parse arguments (very simple implementation)
                args = self._parse_args(args_text)
                
                return verb, args
                
        # No verb found
        return None, {}
        
    def _parse_args(self, args_text: str) -> Dict[str, Any]:
        """
        Parse arguments from text.
        
        This is a very simple implementation that looks for key-value pairs.
        A more sophisticated implementation would use NLP techniques.
        
        Args:
            args_text: The text containing arguments.
            
        Returns:
            Dictionary of argument names to values.
        """
        args = {}
        
        # Try to extract key-value pairs
        # This is a very simple implementation
        key_value_pattern = r'--(\w+)=([^\s]+)'
        for match in re.finditer(key_value_pattern, args_text):
            key = match.group(1)
            value = match.group(2)
            
            # Convert value to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
                
            args[key] = value
            
        # If no key-value pairs found, use the whole text as a generic argument
        if not args and args_text:
            # Try to determine what the argument might be
            # For simplicity, assume it's a path or pattern
            if '/' in args_text or '*' in args_text:
                args['path'] = args_text
            else:
                args['text'] = args_text
                
        return args


# Global plugin manager
plugin_manager = PluginManager()
