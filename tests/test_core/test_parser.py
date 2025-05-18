from unittest.mock import MagicMock

import pytest

from plainspeak.config import PlainSpeakConfig
from plainspeak.context import PlainSpeakContext
from plainspeak.core.llm import LLMInterface
from plainspeak.core.parser import Parser
from plainspeak.plugins.manager import PluginManager


@pytest.fixture
def mock_config():
    return MagicMock(spec=PlainSpeakConfig)


@pytest.fixture
def mock_llm_interface():
    mock = MagicMock(spec=LLMInterface)
    # Configure a default return value for parse_intent
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
def mock_plugin_manager():
    mock = MagicMock(spec=PluginManager)
    # Mock the get_plugin method to return a mock plugin if needed
    mock_plugin = MagicMock()
    mock_plugin.name = "test_plugin"
    mock_plugin.get_verb_details.return_value = {
        "template": "echo {param1}",
        "action_type": "execute_command",
        "parameters": {"param1": {"type": "string", "required": True}},
    }
    mock.get_plugin.return_value = mock_plugin
    mock.find_plugin_for_verb.return_value = mock_plugin
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
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test successful parsing when LLM provides a valid intent and plugin manager resolves it."""
        test_command = "do a test thing"

        # LLM returns a valid AST
        mock_ast_from_llm = {
            "verb": "test_verb",
            "plugin_hint": "test_plugin",  # LLM might suggest a plugin
            "args": {"param1": "value1"},
            "confidence": 0.95,
            "original_text": test_command,
            "parameters": {"param1": "value1"},  # Parameters extracted by LLM
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        # Plugin manager successfully finds the plugin and verb
        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"
        verb_details = {
            "template": "echo {param1}",
            "action_type": "execute_command",
            "parameters_schema": {"param1": {"type": "string", "required": True}},  # Simplified schema
        }
        mock_plugin.get_verb_details.return_value = verb_details
        mock_plugin_manager.find_plugin_for_verb.return_value = mock_plugin
        mock_plugin_manager.resolve_parameters.return_value = (
            {"param1": "value1"},
            [],
        )  # Resolved params, empty missing params

        result_ast = parser_instance.parse(test_command, mock_context)

        mock_llm_interface.parse_intent.assert_called_once_with(test_command, mock_context)
        mock_plugin_manager.find_plugin_for_verb.assert_called_once_with("test_verb", "test_plugin")
        mock_plugin_manager.resolve_parameters.assert_called_once()

        assert result_ast is not None
        assert not isinstance(result_ast, str)  # Should not be an error string
        assert result_ast["verb"] == "test_verb"
        assert result_ast["plugin"] == "test_plugin"
        assert result_ast["command_template"] == verb_details["template"]
        assert result_ast["action_type"] == verb_details["action_type"]
        assert result_ast["parameters"] == {"param1": "value1"}

    def test_parse_llm_fails_to_parse(
        self, parser_instance: Parser, mock_llm_interface: MagicMock, mock_context: MagicMock
    ):
        """Test parsing when the LLM interface returns None (cannot parse intent)."""
        test_command = "gibberish command"
        mock_llm_interface.parse_intent.return_value = None  # LLM fails

        result = parser_instance.parse(test_command, mock_context)

        mock_llm_interface.parse_intent.assert_called_once_with(test_command, mock_context)
        assert isinstance(result, str)
        assert "Could not understand" in result

    def test_parse_plugin_not_found(
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test parsing when LLM provides intent but no plugin is found."""
        test_command = "do something with unknown_plugin"
        mock_ast_from_llm = {
            "verb": "some_verb",
            "plugin_hint": "unknown_plugin",
            "args": {},
            "confidence": 0.9,
            "original_text": test_command,
            "parameters": {},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm
        mock_plugin_manager.find_plugin_for_verb.return_value = None  # Plugin not found

        result = parser_instance.parse(test_command, mock_context)

        mock_llm_interface.parse_intent.assert_called_once_with(test_command, mock_context)
        mock_plugin_manager.find_plugin_for_verb.assert_called_once_with("some_verb", "unknown_plugin")
        assert isinstance(result, str)
        assert "No plugin found for verb" in result

    def test_parse_verb_not_found_in_plugin(
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test parsing when plugin is found but verb is not defined in it."""
        test_command = "use test_plugin to do_unknown_verb"
        mock_ast_from_llm = {
            "verb": "do_unknown_verb",
            "plugin_hint": "test_plugin",
            "args": {},
            "confidence": 0.9,
            "original_text": test_command,
            "parameters": {},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"
        mock_plugin.get_verb_details.return_value = None  # Verb not found in plugin
        mock_plugin_manager.find_plugin_for_verb.return_value = mock_plugin

        result = parser_instance.parse(test_command, mock_context)

        assert isinstance(result, str)
        assert "Verb 'do_unknown_verb' not found in plugin 'test_plugin'" in result

    def test_parse_missing_required_parameters(
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test parsing when required parameters are missing."""
        test_command = "test_verb without required param"
        mock_ast_from_llm = {
            "verb": "test_verb",
            "plugin_hint": "test_plugin",
            "args": {},
            "confidence": 0.9,
            "original_text": test_command,
            "parameters": {},  # Missing param1
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"
        verb_details = {
            "template": "echo {param1}",
            "action_type": "execute_command",
            "parameters_schema": {"param1": {"type": "string", "required": True}},
        }
        mock_plugin.get_verb_details.return_value = verb_details
        mock_plugin_manager.find_plugin_for_verb.return_value = mock_plugin
        # Simulate resolve_parameters returning missing parameters
        mock_plugin_manager.resolve_parameters.return_value = ({}, ["param1"])

        result = parser_instance.parse(test_command, mock_context)

        assert isinstance(result, str)
        assert "Missing required parameter(s) for verb 'test_verb': param1" in result

    def test_parse_llm_returns_low_confidence_ast(
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test parsing when LLM returns an AST but with low confidence.
        The parser should still process it, and the confidence should be in the final AST.
        Higher-level logic (e.g., REPL) might use this confidence score.
        """
        test_command = "do a low confidence thing"
        low_confidence_score = 0.4

        mock_ast_from_llm = {
            "verb": "low_conf_verb",
            "plugin_hint": "test_plugin",
            "args": {"p": "v"},
            "confidence": low_confidence_score,
            "original_text": test_command,
            "parameters": {"p": "v"},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        mock_plugin = MagicMock()
        mock_plugin.name = "test_plugin"
        verb_details = {
            "template": "echo {p}",
            "action_type": "execute_command",
            "parameters_schema": {"p": {"type": "string", "required": True}},
        }
        mock_plugin.get_verb_details.return_value = verb_details
        mock_plugin_manager.find_plugin_for_verb.return_value = mock_plugin
        mock_plugin_manager.resolve_parameters.return_value = ({"p": "v"}, [])

        result_ast = parser_instance.parse(test_command, mock_context)

        assert result_ast is not None
        assert not isinstance(result_ast, str)
        assert result_ast["verb"] == "low_conf_verb"
        assert result_ast["plugin"] == "test_plugin"
        assert result_ast["confidence"] == low_confidence_score  # Verify confidence is propagated
        assert result_ast["parameters"] == {"p": "v"}
        mock_llm_interface.parse_intent.assert_called_once_with(test_command, mock_context)

    def test_parse_context_passed_to_dependencies(
        self,
        parser_instance: Parser,
        mock_llm_interface: MagicMock,
        mock_plugin_manager: MagicMock,
        mock_context: MagicMock,
    ):
        """Test that the context object is correctly passed to LLM and PluginManager."""
        test_command = "do something with context"

        mock_ast_from_llm = {
            "verb": "context_verb",
            "plugin_hint": "context_plugin",
            "args": {"data": "d"},
            "confidence": 0.9,
            "original_text": test_command,
            "parameters": {"data": "d"},
        }
        mock_llm_interface.parse_intent.return_value = mock_ast_from_llm

        mock_plugin = MagicMock()
        mock_plugin.name = "context_plugin"
        verb_details = {
            "template": "cmd {data}",
            "action_type": "execute_command",
            "parameters_schema": {"data": {"type": "string"}},
        }
        mock_plugin.get_verb_details.return_value = verb_details
        mock_plugin_manager.find_plugin_for_verb.return_value = mock_plugin
        mock_plugin_manager.resolve_parameters.return_value = ({"data": "d_resolved"}, [])

        parser_instance.parse(test_command, mock_context)

        # Check if parse_intent was called with the mock_context
        mock_llm_interface.parse_intent.assert_called_once_with(test_command, mock_context)

        # Check if resolve_parameters was called with the mock_context
        # The actual call is: self.plugin_manager.resolve_parameters(plugin, llm_ast.get("parameters", {}), context)
        # So, we need to check the third argument of the call.
        assert mock_plugin_manager.resolve_parameters.call_args is not None
        args, _ = mock_plugin_manager.resolve_parameters.call_args
        assert args[2] == mock_context

    # TODO: Add more tests for different scenarios, e.g.,
    # - Parameter type mismatches (if Parser handles this, or if it's PluginManager's role)
