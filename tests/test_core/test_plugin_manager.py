import importlib.metadata
from unittest.mock import MagicMock, mock_open, patch

import pytest
import yaml

from plainspeak.config import PlainSpeakConfig
from plainspeak.context import PlainSpeakContext
from plainspeak.plugins.base import BasePlugin, PluginLoadError
from plainspeak.plugins.manager import PluginManager
from plainspeak.plugins.schemas import PluginManifest, VerbDetails


@pytest.fixture
def mock_config():
    config = MagicMock(spec=PlainSpeakConfig)
    config.plugins_dir = "dummy_plugins_dir"  # For YAML plugin loading tests
    config.plugins_enabled = ["core_file", "core_system", "yaml_test"]
    config.plugins_disabled = []
    config.plugin_verb_match_threshold = 0.8
    return config


@pytest.fixture
def mock_context():
    return MagicMock(spec=PlainSpeakContext)


# --- Mocks for entry point loading ---
class MockEntryPoint:
    def __init__(self, name, module_name, class_name):
        self.name = name
        self.module_name = module_name
        self.attr = class_name
        self.value = f"{module_name}.{class_name}"

    def load(self):
        # Simulate loading a plugin class
        if self.name == "core_file":
            mock_plugin_class = MagicMock(spec=BasePlugin)
            mock_plugin_instance = MagicMock(spec=BasePlugin)
            mock_plugin_instance.name = "core_file"
            mock_plugin_instance.manifest = MagicMock(spec=PluginManifest)
            mock_plugin_instance.manifest.name = "core_file"
            mock_plugin_instance.manifest.version = "1.0"
            mock_plugin_instance.manifest.description = "File operations"
            mock_plugin_instance.manifest.verbs = {
                "list": VerbDetails(template="ls {path}", parameters_schema={"path": {"type": "string"}})
            }
            mock_plugin_instance.get_verb_details.return_value = mock_plugin_instance.manifest.verbs["list"]
            mock_plugin_class.return_value = mock_plugin_instance
            return mock_plugin_class
        elif self.name == "core_system":
            mock_plugin_class = MagicMock(spec=BasePlugin)
            mock_plugin_instance = MagicMock(spec=BasePlugin)
            mock_plugin_instance.name = "core_system"
            # ... (similar setup)
            mock_plugin_class.return_value = mock_plugin_instance
            return mock_plugin_class
        raise ModuleNotFoundError(f"No module named {self.module_name}")


@pytest.fixture
def mock_entry_points():
    return [
        MockEntryPoint(name="core_file", module_name="plainspeak.plugins.file", class_name="FilePlugin"),
        MockEntryPoint(name="core_system", module_name="plainspeak.plugins.system", class_name="SystemPlugin"),
    ]


# --- End Mocks for entry point loading ---


@pytest.fixture
def plugin_manager_instance(mock_config):
    return PluginManager(config=mock_config)


class TestPluginManager:

    @patch("importlib.metadata.entry_points")
    def test_load_plugins_from_entry_points_successful(
        self, mock_eps, mock_config, plugin_manager_instance: PluginManager
    ):
        mock_eps.return_value = {
            "plainspeak.plugins": [
                MockEntryPoint(name="core_file", module_name="plainspeak.plugins.file", class_name="FilePlugin")
            ]
        }

        # Temporarily disable YAML loading for this test or ensure it doesn't interfere
        with patch.object(plugin_manager_instance, "_load_yaml_plugins", MagicMock()):
            plugin_manager_instance.load_plugins()

        assert "core_file" in plugin_manager_instance.plugins
        assert plugin_manager_instance.plugins["core_file"].name == "core_file"
        mock_eps.assert_called_once_with(group="plainspeak.plugins")

    @patch("importlib.metadata.entry_points", side_effect=Exception("Entry point error"))
    def test_load_plugins_from_entry_points_general_error(self, mock_eps_error, plugin_manager_instance: PluginManager):
        with patch.object(plugin_manager_instance, "_load_yaml_plugins", MagicMock()):
            with pytest.raises(PluginLoadError, match="Error loading plugins from entry points"):
                plugin_manager_instance.load_plugins()

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    def test_load_yaml_plugins_successful(
        self, mock_yaml_load, mock_file_open, mock_listdir, mock_path_exists, mock_config
    ):
        mock_path_exists.return_value = True  # plugins_dir exists
        mock_listdir.return_value = ["yaml_test.yaml", "another.yml"]

        # Mock content for yaml_test.yaml
        yaml_content_test = {
            "name": "yaml_test",
            "version": "0.1",
            "description": "A YAML test plugin",
            "verbs": {"test_verb": {"template": "echo test", "parameters_schema": {}}},
        }
        # Mock content for another.yml (will be skipped if not in enabled_plugins)
        yaml_content_another = {
            "name": "another_yaml",
            "version": "0.1",
            "description": "Another YAML plugin",
            "verbs": {"another_verb": {"template": "echo another"}},
        }

        # Configure yaml.safe_load to return different content based on file path
        def yaml_side_effect(stream):
            if "yaml_test.yaml" in stream.name:
                return yaml_content_test
            elif "another.yml" in stream.name:  # This plugin is not in enabled_plugins
                return yaml_content_another
            return None

        mock_yaml_load.side_effect = yaml_side_effect

        # Configure open to simulate reading different files
        def open_side_effect(path, *args, **kwargs):
            if "yaml_test.yaml" in path:
                return mock_open(read_data=yaml.dump(yaml_content_test))().__enter__()
            elif "another.yml" in path:
                return mock_open(read_data=yaml.dump(yaml_content_another))().__enter__()
            raise FileNotFoundError

        mock_file_open.side_effect = open_side_effect

        manager = PluginManager(config=mock_config)  # Re-init with potentially updated config
        with patch.object(manager, "_load_entry_point_plugins", MagicMock()):  # Isolate YAML loading
            manager.load_plugins()

        assert "yaml_test" in manager.plugins
        assert manager.plugins["yaml_test"].name == "yaml_test"
        assert "another_yaml" not in manager.plugins  # Because it's not in enabled_plugins

    def test_find_plugin_for_verb_exact_match(self, plugin_manager_instance: PluginManager):
        # Setup a mock plugin
        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "test_plugin"
        mock_plugin.has_verb.return_value = True
        mock_plugin.get_verb_details.return_value = VerbDetails(template="cmd {arg}", parameters_schema={})

        plugin_manager_instance.plugins = {"test_plugin": mock_plugin}
        plugin_manager_instance.verb_to_plugin_map = {"test_verb": ["test_plugin"]}

        found_plugin = plugin_manager_instance.find_plugin_for_verb("test_verb")
        assert found_plugin == mock_plugin

    def test_find_plugin_for_verb_no_match(self, plugin_manager_instance: PluginManager):
        plugin_manager_instance.verb_to_plugin_map = {}
        found_plugin = plugin_manager_instance.find_plugin_for_verb("nonexistent_verb")
        assert found_plugin is None

    @patch("difflib.get_close_matches")
    def test_find_plugin_for_verb_fuzzy_match(
        self, mock_get_close_matches, plugin_manager_instance: PluginManager, mock_config
    ):
        mock_config.plugin_verb_match_threshold = 0.7  # Ensure fuzzy matching is considered

        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "fuzzy_plugin"
        mock_plugin.has_verb.return_value = True  # Assume it has the verb once matched
        mock_plugin.get_verb_details.return_value = VerbDetails(template="fuzzy_cmd", parameters_schema={})

        plugin_manager_instance.plugins = {"fuzzy_plugin": mock_plugin}
        plugin_manager_instance.verb_to_plugin_map = {"actual_verb": ["fuzzy_plugin"]}  # Map for the actual verb

        # Simulate get_close_matches returning 'actual_verb' for 'actul_verb'
        mock_get_close_matches.return_value = ["actual_verb"]

        found_plugin = plugin_manager_instance.find_plugin_for_verb("actul_verb")  # User types 'actul_verb'

        assert found_plugin == mock_plugin
        mock_get_close_matches.assert_called_once_with(
            "actul_verb", ["actual_verb"], n=1, cutoff=mock_config.plugin_verb_match_threshold
        )

    def test_resolve_parameters_successful(self, plugin_manager_instance: PluginManager, mock_context):
        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "param_plugin"
        # Simplified schema: param1 is required, param2 is optional with default
        verb_schema = {
            "param1": {"type": "string", "required": True},
            "param2": {"type": "integer", "required": False, "default": 100},
            "param3": {"type": "string", "required": False},
        }

        llm_params = {"param1": "hello", "param3": "world"}  # param2 missing, should use default

        resolved_params, missing_params = plugin_manager_instance.resolve_parameters(
            mock_plugin, verb_schema, llm_params, mock_context
        )

        assert not missing_params  # No missing required params
        assert resolved_params["param1"] == "hello"
        assert resolved_params["param2"] == 100  # Default value used
        assert resolved_params["param3"] == "world"

    def test_resolve_parameters_missing_required(self, plugin_manager_instance: PluginManager, mock_context):
        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "param_plugin"
        verb_schema = {"param1": {"type": "string", "required": True}, "param2": {"type": "string", "required": True}}
        llm_params = {"param1": "value1"}  # param2 is missing

        resolved_params, missing_params = plugin_manager_instance.resolve_parameters(
            mock_plugin, verb_schema, llm_params, mock_context
        )
        assert "param2" in missing_params
        assert resolved_params["param1"] == "value1"

    def test_get_plugin_exists(self, plugin_manager_instance: PluginManager):
        mock_plugin = MagicMock()
        mock_plugin.name = "existing_plugin"
        plugin_manager_instance.plugins = {"existing_plugin": mock_plugin}

        assert plugin_manager_instance.get_plugin("existing_plugin") == mock_plugin

    def test_get_plugin_not_exists(self, plugin_manager_instance: PluginManager):
        plugin_manager_instance.plugins = {}
        assert plugin_manager_instance.get_plugin("non_existing_plugin") is None

    @patch("importlib.metadata.entry_points")
    def test_plugin_disabling(self, mock_eps, mock_config: MagicMock):
        # Configure a plugin to be disabled
        mock_config.plugins_enabled = ["core_file", "plugin_to_disable"]
        mock_config.plugins_disabled = ["plugin_to_disable"]

        # Mock entry points to provide 'core_file' and 'plugin_to_disable'
        mock_entry_point_file = MockEntryPoint(
            name="core_file", module_name="plainspeak.plugins.file", class_name="FilePlugin"
        )

        # Mock for the plugin that will be disabled
        mock_plugin_class_disabled = MagicMock(spec=BasePlugin)
        mock_plugin_instance_disabled = MagicMock(spec=BasePlugin)
        mock_plugin_instance_disabled.name = "plugin_to_disable"
        mock_plugin_instance_disabled.manifest = MagicMock(
            spec=PluginManifest, name="plugin_to_disable", version="1.0", description="Disabled plugin", verbs={}
        )
        mock_plugin_class_disabled.return_value = mock_plugin_instance_disabled

        mock_entry_point_disabled = MagicMock(spec=importlib.metadata.EntryPoint)
        mock_entry_point_disabled.name = "plugin_to_disable"
        mock_entry_point_disabled.load.return_value = mock_plugin_class_disabled

        mock_eps.return_value = {"plainspeak.plugins": [mock_entry_point_file, mock_entry_point_disabled]}

        manager = PluginManager(config=mock_config)
        with patch.object(manager, "_load_yaml_plugins", MagicMock()):  # Isolate entry point loading
            manager.load_plugins()

        assert "core_file" in manager.plugins
        assert "plugin_to_disable" not in manager.plugins
        assert "plugin_to_disable" not in manager.verb_to_plugin_map  # Ensure its verbs are not mapped

    def test_resolve_parameters_with_context_variable(
        self, plugin_manager_instance: PluginManager, mock_context: MagicMock
    ):
        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "context_param_plugin"
        # param1 required, param2 uses context variable if not provided by LLM
        verb_schema = {
            "param1": {"type": "string", "required": True},
            "param2": {"type": "string", "required": False, "context_var": "user_home_dir"},
        }

        llm_params = {"param1": "some_file.txt"}  # param2 not provided by LLM
        mock_context.get_variable.return_value = "/users/testuser"  # Context provides user_home_dir

        resolved_params, missing_params = plugin_manager_instance.resolve_parameters(
            mock_plugin, verb_schema, llm_params, mock_context
        )

        assert not missing_params
        assert resolved_params["param1"] == "some_file.txt"
        assert resolved_params["param2"] == "/users/testuser"  # Value from context
        mock_context.get_variable.assert_called_once_with("user_home_dir")

    def test_resolve_parameters_context_variable_overridden_by_llm(
        self, plugin_manager_instance: PluginManager, mock_context: MagicMock
    ):
        mock_plugin = MagicMock(spec=BasePlugin)
        verb_schema = {"path": {"type": "string", "required": False, "context_var": "current_directory"}}
        llm_params = {"path": "/provided/path"}  # LLM provides the path
        mock_context.get_variable.return_value = "/default/context/path"

        resolved_params, _ = plugin_manager_instance.resolve_parameters(
            mock_plugin, verb_schema, llm_params, mock_context
        )
        assert resolved_params["path"] == "/provided/path"  # LLM value takes precedence
        mock_context.get_variable.assert_not_called()  # Context var should not be fetched if LLM provides it

    def test_find_plugin_for_verb_with_alias(self, plugin_manager_instance: PluginManager):
        # Setup a mock plugin with an alias
        mock_plugin = MagicMock(spec=BasePlugin)
        mock_plugin.name = "alias_plugin"

        list_verb_details = VerbDetails(
            template="ls {path}",
            parameters_schema={"path": {"type": "string"}},
            aliases=["ll", "list_files"],  # Define aliases
        )
        mock_plugin.manifest = MagicMock(spec=PluginManifest, verbs={"list": list_verb_details})
        mock_plugin.get_verb_details.return_value = list_verb_details  # if called with 'list'

        # Simulate how _build_verb_map would populate verb_to_plugin_map
        plugin_manager_instance.plugins = {"alias_plugin": mock_plugin}
        plugin_manager_instance.verb_to_plugin_map = {
            "list": ["alias_plugin"],
            "ll": ["alias_plugin"],  # Alias mapped
            "list_files": ["alias_plugin"],  # Another alias mapped
        }

        # To make find_plugin_for_verb work correctly, it also checks plugin.has_verb(verb_name)
        # The verb_name passed to has_verb will be the canonical one ('list') after alias resolution.
        def mock_has_verb(verb_name):
            return verb_name == "list"

        mock_plugin.has_verb.side_effect = mock_has_verb

        found_plugin_by_alias1 = plugin_manager_instance.find_plugin_for_verb("ll")
        assert found_plugin_by_alias1 == mock_plugin

        found_plugin_by_alias2 = plugin_manager_instance.find_plugin_for_verb("list_files")
        assert found_plugin_by_alias2 == mock_plugin

        found_plugin_by_canonical = plugin_manager_instance.find_plugin_for_verb("list")
        assert found_plugin_by_canonical == mock_plugin

    def test_find_plugin_for_verb_with_priority(self, mock_config):
        """Test that plugin priority is respected when multiple plugins define the same verb."""
        manager = PluginManager(config=mock_config)

        # Plugin 1: Lower priority (default 0)
        plugin1_verb_details = VerbDetails(template="cmd1 {arg}", parameters_schema={})
        plugin1_manifest = MagicMock(
            spec=PluginManifest,
            name="plugin1",
            version="1.0",
            description="P1",
            verbs={"clash_verb": plugin1_verb_details},
            priority=0,
        )  # Default priority
        mock_plugin1 = MagicMock(spec=BasePlugin, name="plugin1", manifest=plugin1_manifest)
        mock_plugin1.get_verb_details.return_value = plugin1_verb_details
        mock_plugin1.has_verb.return_value = True

        # Plugin 2: Higher priority
        plugin2_verb_details = VerbDetails(template="cmd2 {arg}", parameters_schema={})
        plugin2_manifest = MagicMock(
            spec=PluginManifest,
            name="plugin2",
            version="1.0",
            description="P2",
            verbs={"clash_verb": plugin2_verb_details},
            priority=10,
        )  # Higher priority
        mock_plugin2 = MagicMock(spec=BasePlugin, name="plugin2", manifest=plugin2_manifest)
        mock_plugin2.get_verb_details.return_value = plugin2_verb_details
        mock_plugin2.has_verb.return_value = True

        manager.plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}
        manager._build_verb_map()  # Rebuild map with these plugins

        found_plugin = manager.find_plugin_for_verb("clash_verb")
        assert found_plugin == mock_plugin2  # Plugin2 should be chosen due to higher priority

    def test_find_plugin_for_verb_core_plugin_priority(self, mock_config):
        """Test that core plugins are prioritized over non-core if priorities are equal."""
        manager = PluginManager(config=mock_config)

        # Core Plugin (name starts with 'core_')
        core_verb_details = VerbDetails(template="core_cmd {arg}", parameters_schema={})
        core_manifest = MagicMock(
            spec=PluginManifest,
            name="core_test",
            version="1.0",
            description="CoreP",
            verbs={"clash_verb": core_verb_details},
            priority=5,
        )
        mock_core_plugin = MagicMock(spec=BasePlugin, name="core_test", manifest=core_manifest)
        mock_core_plugin.get_verb_details.return_value = core_verb_details
        mock_core_plugin.has_verb.return_value = True

        # Non-Core Plugin with same priority
        non_core_verb_details = VerbDetails(template="noncore_cmd {arg}", parameters_schema={})
        non_core_manifest = MagicMock(
            spec=PluginManifest,
            name="custom_test",
            version="1.0",
            description="CustomP",
            verbs={"clash_verb": non_core_verb_details},
            priority=5,
        )
        mock_non_core_plugin = MagicMock(spec=BasePlugin, name="custom_test", manifest=non_core_manifest)
        mock_non_core_plugin.get_verb_details.return_value = non_core_verb_details
        mock_non_core_plugin.has_verb.return_value = True

        manager.plugins = {"core_test": mock_core_plugin, "custom_test": mock_non_core_plugin}
        manager._build_verb_map()

        found_plugin = manager.find_plugin_for_verb("clash_verb")
        assert found_plugin == mock_core_plugin  # Core plugin should win

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load")
    @patch("plainspeak.plugins.yaml_plugin.YAMLPlugin.validate_manifest")  # To simulate validation error
    def test_load_yaml_plugins_schema_validation_error(
        self,
        mock_validate_manifest,
        mock_yaml_load,
        mock_file_open,
        mock_listdir,
        mock_path_exists,
        mock_config,
        caplog,
    ):
        mock_path_exists.return_value = True
        mock_listdir.return_value = ["invalid_plugin.yaml"]

        yaml_content_invalid = {
            "name": "invalid_plugin",
            "version": "0.1",
            "description": "Invalid schema",
        }  # Missing 'verbs'
        mock_yaml_load.return_value = yaml_content_invalid
        mock_file_open.return_value = mock_open(read_data=yaml.dump(yaml_content_invalid))().__enter__()

        # Simulate Pydantic ValidationError during YAMLPlugin's manifest validation
        from pydantic import ValidationError

        mock_validate_manifest.side_effect = ValidationError.from_exception_data(title="ManifestError", line_errors=[])

        manager = PluginManager(config=mock_config)
        with patch.object(manager, "_load_entry_point_plugins", MagicMock()):
            manager.load_plugins()  # Should not raise, but log an error

        assert "invalid_plugin" not in manager.plugins
        assert "Error validating manifest for YAML plugin invalid_plugin.yaml" in caplog.text
        assert "ManifestError" in caplog.text  # Check for Pydantic error details in log

    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_load", side_effect=yaml.YAMLError("Bad YAML format"))
    def test_load_yaml_plugins_invalid_yaml_content(
        self, mock_yaml_error, mock_file_open, mock_listdir, mock_path_exists, mock_config, caplog
    ):
        mock_path_exists.return_value = True
        mock_listdir.return_value = ["broken.yaml"]
        mock_file_open.return_value = mock_open(
            read_data="name: broken\nversion: 0.1\n  bad_indent: true"
        )().__enter__()

        manager = PluginManager(config=mock_config)
        with patch.object(manager, "_load_entry_point_plugins", MagicMock()):
            manager.load_plugins()

        assert "broken" not in manager.plugins
        assert "Error loading YAML plugin from broken.yaml: Bad YAML format" in caplog.text

    # TODO:
    # - Test _build_verb_map more directly
    # if complex priority/aliasing scenarios are hard to test via find_plugin_for_verb
