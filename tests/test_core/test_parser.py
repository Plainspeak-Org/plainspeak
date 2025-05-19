"""Test the core parser functionality."""

from unittest.mock import MagicMock

import pytest

from plainspeak.config import PlainSpeakConfig
from plainspeak.context import PlainSpeakContext
from plainspeak.core.llm import LLMInterface
from plainspeak.core.parser import Parser
from plainspeak.plugins.base import BasePlugin, PluginRegistry


class MockPlugin(BasePlugin):
    """Mock plugin for testing."""

    def __init__(self):
        super().__init__("test_plugin", "Test plugin", priority=0)
        self.verb_details = {
            "test_verb": {
                "template": "echo {param1}",
                "action_type": "execute_command",
                "parameters": {"param1": {"type": "string", "required": True}},
            }
        }

    def get_verbs(self) -> list:
        return ["test_verb"]

    def generate_command(self, verb: str, args: dict) -> str:
        return f"echo {args.get('param1', '')}"

    def get_verb_details(self, verb: str) -> dict:
        """Get details for a verb."""
        return self.verb_details.get(verb, {})


@pytest.fixture
def mock_config():
    return MagicMock(spec=PlainSpeakConfig)


@pytest.fixture
def mock_llm_interface():
    mock = MagicMock(spec=LLMInterface)
    mock.parse_intent.return_value = {
        "verb": "test_verb",
        "plugin": "test_plugin",
        "args": {"param1": "value1"},
        "confidence": 0.95,
        "original_text": "do a test thing",
        "action_type": "execute_command",
        "command_template": "echo {param1}",
        "parameters": {"param1": "value1"},
    }
    return mock


@pytest.fixture
def mock_plugin():
    return MockPlugin()


@pytest.fixture
def mock_plugin_registry(mock_plugin):
    registry = MagicMock(spec=PluginRegistry)
    registry.get_plugin.return_value = mock_plugin
    registry.get_plugin_for_verb.return_value = mock_plugin
    registry.get_all_verbs.return_value = {"test_verb": "test_plugin"}
    registry.plugins = {"test_plugin": mock_plugin}
    return registry


@pytest.fixture
def mock_plugin_manager(mock_plugin, mock_plugin_registry):
    mock = MagicMock()  # Remove spec to allow adding methods
    mock.registry = mock_plugin_registry
    mock.get_plugin.return_value = mock_plugin
    mock.get_plugin_for_verb.return_value = mock_plugin
    mock.get_all_verbs.return_value = {"test_verb": "test_plugin"}
    mock.generate_command.return_value = (True, "echo value1")
    mock.find_plugin_for_verb = MagicMock(return_value=mock_plugin)

    # Add method to resolve parameters
    def resolve_params(plugin, params, context=None):
        if not params:
            return {}, ["param1"]
        return params, []

    mock.resolve_parameters = resolve_params

    return mock


@pytest.fixture
def mock_context():
    return MagicMock(spec=PlainSpeakContext)


@pytest.fixture
def parser_instance(mock_config, mock_plugin_manager, mock_llm_interface):
    return Parser(config=mock_config, plugin_manager=mock_plugin_manager, llm_interface=mock_llm_interface)


class TestParser:
    def test_parser_initialization(self, mock_config, mock_plugin_manager, mock_llm_interface):
        """Test that the Parser initializes correctly."""
        parser = Parser(config=mock_config, plugin_manager=mock_plugin_manager, llm_interface=mock_llm_interface)
        assert parser.config == mock_config
        assert parser.plugin_manager == mock_plugin_manager
        assert parser.llm == mock_llm_interface

    def test_parse_successful_intent_resolution(
        self, parser_instance, mock_llm_interface, mock_plugin_manager, mock_context
    ):
        """Test successful parsing when LLM provides a valid intent."""
        # Configure expected response
        test_command = "do a test thing"
        expected_result = {
            "verb": "test_verb",
            "args": {"param1": "value1"},
            "confidence": 0.95,
            "original_text": test_command,
            "command_template": "echo {param1}",
            "action_type": "execute_command",
            "parameters": {"param1": "value1"},
            "plugin": "test_plugin",
        }

        # Set up mocks
        # Set up plugin mock with correct name
        plugin_with_name = MagicMock()
        plugin_with_name.name = "test_plugin"
        mock_plugin_manager.find_plugin_for_verb.return_value = plugin_with_name

        # Set up LLM mock response
        mock_ast_from_llm = expected_result.copy()
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        # Test
        result = parser_instance.parse(test_command, mock_context)

        # Verify result
        assert isinstance(result, dict)
        assert result["verb"] == expected_result["verb"]
        assert result["plugin"] == expected_result["plugin"]
        assert result["parameters"] == expected_result["parameters"]

    def test_parse_llm_fails_to_parse(self, parser_instance, mock_llm_interface, mock_context):
        """Test parsing when the LLM interface cannot parse intent."""
        test_command = "gibberish command"
        mock_llm_interface.parse_intent.return_value = None
        result = parser_instance.parse(test_command, mock_context)

        assert isinstance(result, str)
        assert "Could not understand" in result

    def test_parse_missing_required_parameters(
        self, parser_instance, mock_llm_interface, mock_plugin_manager, mock_context
    ):
        """Test parsing when required parameters are missing."""
        test_command = "test_verb without required param"
        mock_ast_from_llm = {
            "verb": "test_verb",
            "plugin": "test_plugin",
            "args": {},
            "confidence": 0.9,
            "original_text": test_command,
            "parameters": {},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        result = parser_instance.parse(test_command, mock_context)

        assert isinstance(result, str)
        assert "Missing required parameter(s)" in result
        assert "param1" in result

    def test_parse_low_confidence_ast(self, parser_instance, mock_llm_interface, mock_plugin_manager, mock_context):
        """Test parsing with low confidence AST."""
        test_command = "do a low confidence thing"
        mock_ast_from_llm = {
            "verb": "test_verb",
            "plugin": "test_plugin",
            "args": {"param1": "value1"},
            "confidence": 0.4,
            "original_text": test_command,
            "parameters": {"param1": "value1"},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        result = parser_instance.parse(test_command, mock_context)

        assert isinstance(result, dict)
        assert result["verb"] == "test_verb"
        assert abs(result["confidence"] - 0.4) < 1e-6  # Compare with tolerance for floating point
        assert result["parameters"] == {"param1": "value1"}
