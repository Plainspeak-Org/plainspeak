"""Test module for plugin manager."""

from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
import yaml

from plainspeak.config import PlainSpeakConfig
from plainspeak.plugins.base import BasePlugin
from plainspeak.plugins.manager import PluginManager
from plainspeak.utils import paths


# Mock plugin implementations
class MockPluginA(BasePlugin):
    """Mock plugin A for testing."""

    def __init__(self):
        super().__init__(name="plugin_a", description="Test Plugin A", priority=10)
        self._verbs = ["test"]

    def get_verbs(self) -> List[str]:
        return self._verbs

    def get_aliases(self) -> Dict[str, str]:
        return {}

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        return f"{verb} {' '.join(f'{k}={v}' for k, v in args.items())}"


class MockPluginB(BasePlugin):
    """Mock plugin B for testing."""

    def __init__(self):
        super().__init__(name="plugin_b", description="Test Plugin B", priority=10)
        self._verbs = ["test"]

    def get_verbs(self) -> List[str]:
        return self._verbs

    def get_aliases(self) -> Dict[str, str]:
        return {}

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        return f"{verb} {' '.join(f'{k}={v}' for k, v in args.items())}"


class MockPlugin(BasePlugin):
    """Generic mock plugin for testing."""

    def __init__(self, name: str, verbs: List[str], aliases: Dict[str, str]):
        super().__init__(name=name, description="Test plugin", priority=10)
        self._verbs = verbs
        self._aliases = aliases

    def get_verbs(self) -> List[str]:
        return self._verbs

    def get_aliases(self) -> Dict[str, str]:
        return self._aliases

    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        return f"{verb} {' '.join(f'{k}={v}' for k, v in args.items())}"


@pytest.fixture
def mock_base_plugin():
    """Create a mock base plugin."""
    return MockPlugin(name="test_plugin", verbs=["test_verb"], aliases={"tv": "test_verb"})


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock config."""
    config = MagicMock(spec=PlainSpeakConfig)
    config.plugins_dir = str(tmp_path)  # Use temp directory
    config.plugins_enabled = ["core_file", "core_system"]
    config.plugins_disabled = []
    config.plugin_verb_match_threshold = 0.8
    return config


@pytest.fixture
def plugin_manager(mock_config):
    """Create a plugin manager instance."""
    with patch("plainspeak.plugins.manager.PluginManager._load_plugins"):
        manager = PluginManager(config=mock_config)
        # Clear initial plugins for testing
        manager.registry.clear()
        return manager


class TestPluginManager:
    """Test the plugin manager functionality."""

    def test_plugin_initialization(self, plugin_manager, mock_base_plugin):
        """Test that plugins are properly initialized."""
        plugin_manager.registry.register(mock_base_plugin)
        assert "test_plugin" in plugin_manager.registry.plugins
        assert plugin_manager.get_plugin_for_verb("test_verb") == mock_base_plugin

    def test_plugin_verb_matching(self, plugin_manager, mock_base_plugin):
        """Test verb matching functionality."""
        plugin_manager.registry.register(mock_base_plugin)
        assert plugin_manager.get_plugin_for_verb("test_verb") == mock_base_plugin
        assert plugin_manager.get_plugin_for_verb("tv") == mock_base_plugin  # alias
        assert plugin_manager.get_plugin_for_verb("nonexistent") is None

    def test_plugin_priority(self, plugin_manager):
        """Test plugin priority handling."""
        high_priority = MockPlugin(name="high", verbs=["common"], aliases={})
        high_priority.priority = 100

        low_priority = MockPlugin(name="low", verbs=["common"], aliases={})
        low_priority.priority = 1

        plugin_manager.registry.register(low_priority)
        plugin_manager.registry.register(high_priority)

        assert plugin_manager.get_plugin_for_verb("common") == high_priority

    def test_yaml_plugin_loading(self, tmp_path, plugin_manager):
        """Test loading plugins from YAML manifests."""
        plugin_dir = paths.join_paths(str(tmp_path), "plugins")
        paths.make_directory(plugin_dir)

        # Update config to point to our test directory
        plugin_manager.config.plugins_dir = str(plugin_dir)

        manifest_content = {
            "name": "test_yaml_plugin",
            "version": "1.0.0",
            "description": "Test YAML Plugin",
            "author": "Test Author",
            "verbs": ["test", "example"],
            "entrypoint": "test_module.TestPlugin",
            "commands": {
                "test": {
                    "template": "test {arg}",
                    "description": "Run a test command",
                    "examples": ["test arg1"],
                    "required_args": ["arg"],
                    "optional_args": {},
                },
                "example": {
                    "template": "example {arg}",
                    "description": "Run an example command",
                    "examples": ["example arg1"],
                    "required_args": ["arg"],
                    "optional_args": {},
                },
            },
            "verb_aliases": {"test": ["t"], "example": ["ex"]},
        }

        # Create plugins directory and write manifest
        plugin_path = paths.join_paths(plugin_dir, "test_yaml_plugin")
        paths.make_directory(plugin_path)
        manifest_path = paths.join_paths(plugin_path, "manifest.yaml")
        with open(manifest_path, "w") as f:
            yaml.dump(manifest_content, f)

        mock_plugin = MockPlugin(
            name="test_yaml_plugin", verbs=["test", "example"], aliases={"t": "test", "ex": "example"}
        )

        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_plugin_class = MagicMock(return_value=mock_plugin)
            setattr(mock_module, "TestPlugin", mock_plugin_class)
            mock_import.return_value = mock_module

            plugin_manager._load_plugins_from_directories()
            assert "test_yaml_plugin" in plugin_manager.registry.plugins

    def test_plugin_discovery(self, plugin_manager, tmp_path):
        """Test plugin directory scanning."""
        # Set up test plugins directory
        plugin_dir = paths.join_paths(str(tmp_path), "plugins")
        paths.make_directory(plugin_dir)
        plugin_manager.config.plugins_dir = str(plugin_dir)

        # Create plugin directories
        plugin_a_dir = paths.join_paths(plugin_dir, "plugin_a")
        plugin_b_dir = paths.join_paths(plugin_dir, "plugin_b")
        paths.make_directory(plugin_a_dir)
        paths.make_directory(plugin_b_dir)

        # Write manifest files
        manifest_a_content = {
            "name": "plugin_a",
            "version": "1.0.0",
            "description": "Test Plugin A",
            "author": "Test Author",
            "verbs": ["test"],
            "entrypoint": "test_module_a.TestPlugin",
            "commands": {
                "test": {
                    "template": "test {arg}",
                    "description": "Run a test command",
                    "examples": ["test arg1"],
                    "required_args": ["arg"],
                    "optional_args": {},
                }
            },
        }

        manifest_b_content = {
            "name": "plugin_b",
            "version": "1.0.0",
            "description": "Test Plugin B",
            "author": "Test Author",
            "verbs": ["test"],
            "entrypoint": "test_module_b.TestPlugin",
            "commands": {
                "test": {
                    "template": "test {arg}",
                    "description": "Run a test command",
                    "examples": ["test arg1"],
                    "required_args": ["arg"],
                    "optional_args": {},
                }
            },
        }

        manifest_a_path = paths.join_paths(plugin_a_dir, "manifest.yaml")
        manifest_b_path = paths.join_paths(plugin_b_dir, "manifest.yaml")

        with open(manifest_a_path, "w") as f:
            yaml.dump(manifest_a_content, f)
        with open(manifest_b_path, "w") as f:
            yaml.dump(manifest_b_content, f)

        with patch("importlib.import_module") as mock_import:
            mock_import.side_effect = lambda name: MagicMock(
                **{"TestPlugin": MockPluginA if "module_a" in name else MockPluginB}
            )

            plugin_manager._load_plugins_from_directories()
            assert len(plugin_manager.registry.plugins) == 2
            assert "plugin_a" in plugin_manager.registry.plugins
            assert "plugin_b" in plugin_manager.registry.plugins

    def test_plugin_reloading(self, plugin_manager, mock_base_plugin):
        """Test plugin reloading functionality."""
        plugin_manager.registry.register(mock_base_plugin)
        assert "test_plugin" in plugin_manager.registry.plugins

        with patch("plainspeak.plugins.manager.PluginManager._load_plugins"):
            plugin_manager.reload_plugins()
            assert "test_plugin" not in plugin_manager.registry.plugins
