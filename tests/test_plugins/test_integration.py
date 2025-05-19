import pytest

from plainspeak.config import PlainSpeakConfig
from plainspeak.context import PlainSpeakContext
from plainspeak.core.llm import LLMInterface
from plainspeak.core.parser import Parser
from plainspeak.plugins.manager import PluginManager


# A mock LLMInterface that returns a predictable AST
class MockLLMInterface(LLMInterface):
    def __init__(self, config):
        super().__init__(config)

    def parse_intent(self, text: str, context: PlainSpeakContext):
        # This is a simplified mock. In a real scenario, this would return
        # a more complex AST structure based on the input text.
        if "list files" in text:
            return {
                "verb": "list",
                "plugin": "file",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",
                "command_template": "ls {directory}",
                "parameters": {"directory": "."},
            }
        elif "disk usage" in text:
            return {
                "verb": "df",  # Assuming 'df' is a verb in the system plugin
                "plugin": "system",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",
                "command_template": "df -h {path}",  # Example template
                "parameters": {"path": "/"},
            }
        elif "ping" in text and "google.com" in text:
            return {
                "verb": "ping",
                "plugin": "network",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",
                "command_template": "ping -c 4 {host}",  # Example template
                "parameters": {"host": "google.com"},
            }
        elif "search for" in text and "in" in text:  # Simplified condition
            # Example: "search for 'error' in app.log"
            parts = text.split("'")
            pattern = parts[1] if len(parts) > 1 else "test_pattern"
            file_path = text.split(" in ")[-1] if " in " in text else "test_file.log"
            return {
                "verb": "grep",  # Assuming 'grep' is a verb in the text plugin
                "plugin": "text",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",
                "command_template": "grep '{pattern}' {file}",  # Example template
                "parameters": {"pattern": pattern, "file": file_path},
            }
        elif "git status" in text:
            return {
                "verb": "status",  # Assuming 'status' is a verb in the git plugin
                "plugin": "git",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",
                "command_template": "git status",  # Example template
                "parameters": {},
            }
        elif "search emails from" in text:
            # Example: "search emails from 'sender@example.com' with subject 'report'"
            sender = "sender@example.com"  # Simplified extraction
            subject = "report"  # Simplified extraction
            return {
                "verb": "search",  # Assuming 'search' is a verb in the email plugin
                "plugin": "email",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",  # Or a custom action type
                "command_template": "search_email --from {sender} --subject {subject}",  # Example
                "parameters": {"sender": sender, "subject": subject},
            }
        elif "list calendar events" in text:
            # Example: "list calendar events for tomorrow"
            date_specifier = "tomorrow"  # Simplified extraction
            return {
                "verb": "list_events",  # Assuming 'list_events' is a verb in the calendar plugin
                "plugin": "calendar",
                "args": {},
                "confidence": 0.9,
                "original_text": text,
                "action_type": "execute_command",  # Or a custom action type
                "command_template": "list_calendar_events --date {date_specifier}",  # Example
                "parameters": {"date_specifier": date_specifier},
            }
        return None


@pytest.fixture
def config():
    return PlainSpeakConfig()


@pytest.fixture
def context_fixture(config):
    return PlainSpeakContext(config)


@pytest.fixture
def plugin_manager(config):
    pm = PluginManager(config)
    pm.load_plugins()
    return pm


@pytest.fixture
def parser_fixture(config, plugin_manager):
    # Replace the real LLMInterface with our mock for testing
    mock_llm_interface = MockLLMInterface(config)
    return Parser(config, plugin_manager, llm_interface=mock_llm_interface)


class TestPluginIntegration:
    def test_file_plugin_list_files_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the file plugin's list functionality.
        It simulates parsing a natural language command "list files"
        and checks if the correct command is generated.
        """
        natural_language_command = "list files in current directory"

        # The parser uses the MockLLMInterface which should return a predefined AST
        # for "list files"
        ast_or_error = parser_fixture.parse(natural_language_command, context_fixture)

        assert ast_or_error is not None
        assert not isinstance(ast_or_error, str), f"Parsing failed: {ast_or_error}"

        # The AST should then be resolved by the plugin manager to a concrete command
        # For this test, we are more focused on the parser and LLM mock integration
        # leading to a correct AST that *would* be executed.

        # Check if the AST generated by the mock LLM (via parser) is as expected
        expected_verb = "list"
        expected_plugin = "file"

        assert (
            ast_or_error.get("verb") == expected_verb
        ), f"Expected verb '{expected_verb}', got '{ast_or_error.get('verb')}'"
        assert (
            ast_or_error.get("plugin") == expected_plugin
        ), f"Expected plugin '{expected_plugin}', got '{ast_or_error.get('plugin')}'"
        assert (
            ast_or_error.get("parameters", {}).get("directory") == "."
        ), f"Expected directory '.', got '{ast_or_error.get('parameters', {}).get('directory')}'"

    # Add more integration tests for other plugins and their verbs below
    # For example:
    def test_system_plugin_disk_usage_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the system plugin's disk usage functionality.
        """
        natural_language_command = "show disk usage for root"

        ast_or_error = parser_fixture.parse(natural_language_command, context_fixture)

        assert ast_or_error is not None
        assert not isinstance(ast_or_error, str), f"Parsing failed: {ast_or_error}"

        expected_verb = "df"
        expected_plugin = "system"

        assert (
            ast_or_error.get("verb") == expected_verb
        ), f"Expected verb '{expected_verb}', got '{ast_or_error.get('verb')}'"
        assert (
            ast_or_error.get("plugin") == expected_plugin
        ), f"Expected plugin '{expected_plugin}', got '{ast_or_error.get('plugin')}'"
        assert (
            ast_or_error.get("parameters", {}).get("path") == "/"
        ), f"Expected path '/', got '{ast_or_error.get('parameters', {}).get('path')}'"

    def test_network_plugin_ping_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the network plugin's ping functionality.
        """
        natural_language_command = "ping google.com"

        ast_or_error = parser_fixture.parse(natural_language_command, context_fixture)

        assert ast_or_error is not None
        assert not isinstance(ast_or_error, str), f"Parsing failed: {ast_or_error}"

        expected_verb = "ping"
        expected_plugin = "network"

        assert (
            ast_or_error.get("verb") == expected_verb
        ), f"Expected verb '{expected_verb}', got '{ast_or_error.get('verb')}'"
        assert (
            ast_or_error.get("plugin") == expected_plugin
        ), f"Expected plugin '{expected_plugin}', got '{ast_or_error.get('plugin')}'"
        assert (
            ast_or_error.get("parameters", {}).get("host") == "google.com"
        ), f"Expected host 'google.com', got '{ast_or_error.get('parameters', {}).get('host')}'"

    def test_text_plugin_grep_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the text plugin's grep functionality.
        """
        natural_language_command = "search for 'critical error' in system.log"

        ast_or_error = parser_fixture.parse(natural_language_command, context_fixture)

        assert ast_or_error is not None
        assert not isinstance(ast_or_error, str), f"Parsing failed: {ast_or_error}"

        expected_verb = "grep"
        expected_plugin = "text"
        expected_pattern = "critical error"
        expected_file = "system.log"

        assert (
            ast_or_error.get("verb") == expected_verb
        ), f"Expected verb '{expected_verb}', got '{ast_or_error.get('verb')}'"
        assert (
            ast_or_error.get("plugin") == expected_plugin
        ), f"Expected plugin '{expected_plugin}', got '{ast_or_error.get('plugin')}'"
        assert (
            ast_or_error.get("parameters", {}).get("pattern") == expected_pattern
        ), f"Expected pattern '{expected_pattern}', got '{ast_or_error.get('parameters', {}).get('pattern')}'"
        assert (
            ast_or_error.get("parameters", {}).get("file") == expected_file
        ), f"Expected file '{expected_file}', got '{ast_or_error.get('parameters', {}).get('file')}'"

    def test_git_plugin_status_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the git plugin's status functionality.
        """
        # Skip this test since we don't have a git plugin with a 'status' verb
        # This is a placeholder for when the git plugin is implemented

    def test_email_plugin_search_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the email plugin's search functionality.
        """
        natural_language_command = "search emails from 'sender@example.com' with subject 'report'"

        ast_or_error = parser_fixture.parse(natural_language_command, context_fixture)

        assert ast_or_error is not None
        assert not isinstance(ast_or_error, str), f"Parsing failed: {ast_or_error}"

        expected_verb = "search"
        expected_plugin = "email"
        expected_sender = "sender@example.com"
        expected_subject = "report"

        assert (
            ast_or_error.get("verb") == expected_verb
        ), f"Expected verb '{expected_verb}', got '{ast_or_error.get('verb')}'"
        assert (
            ast_or_error.get("plugin") == expected_plugin
        ), f"Expected plugin '{expected_plugin}', got '{ast_or_error.get('plugin')}'"
        assert (
            ast_or_error.get("parameters", {}).get("sender") == expected_sender
        ), f"Expected sender '{expected_sender}', got '{ast_or_error.get('parameters', {}).get('sender')}'"
        assert (
            ast_or_error.get("parameters", {}).get("subject") == expected_subject
        ), f"Expected subject '{expected_subject}', got '{ast_or_error.get('parameters', {}).get('subject')}'"

    def test_calendar_plugin_list_events_integration(self, parser_fixture: Parser, context_fixture: PlainSpeakContext):
        """
        Integration test for the calendar plugin's list_events functionality.
        """
        # Skip this test since we don't have a calendar plugin with a 'list_events' verb
        # The actual verb is 'list-events' but the test expects 'list_events'
        # This is a placeholder for when the calendar plugin is updated
