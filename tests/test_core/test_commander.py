from unittest.mock import MagicMock

import pytest

from plainspeak.config import PlainSpeakConfig
from plainspeak.core.commander import Commander
from plainspeak.core.sandbox import Sandbox, SandboxExecutionError


@pytest.fixture
def mock_config():
    return MagicMock(spec=PlainSpeakConfig)


@pytest.fixture
def mock_sandbox():
    sandbox = MagicMock(spec=Sandbox)
    # Default successful execution
    sandbox.execute_shell_command.return_value = (0, "Success output", None)
    return sandbox


@pytest.fixture
def commander_instance(mock_config, mock_sandbox):
    return Commander(config=mock_config, sandbox=mock_sandbox)


class TestCommander:
    def test_commander_initialization(self, mock_config, mock_sandbox):
        commander = Commander(config=mock_config, sandbox=mock_sandbox)
        assert commander.config == mock_config
        assert commander.sandbox == mock_sandbox

    def test_execute_successful_shell_command(self, commander_instance: Commander, mock_sandbox: MagicMock):
        ast = {
            "command_template": "echo {message}",
            "parameters": {"message": "Hello World"},
            "action_type": "execute_command",
            "plugin": "test_plugin",
            "verb": "echo_verb",
        }
        expected_command = "echo Hello World"
        mock_sandbox.execute_shell_command.return_value = (0, "Hello World output", None)

        success, output, error = commander_instance.execute(ast)

        assert success is True
        assert output == "Hello World output"
        assert error is None
        mock_sandbox.execute_shell_command.assert_called_once_with(expected_command)

    def test_execute_shell_command_failure(self, commander_instance: Commander, mock_sandbox: MagicMock):
        ast = {
            "command_template": "failing_command {arg}",
            "parameters": {"arg": "test"},
            "action_type": "execute_command",
        }
        expected_command = "failing_command test"
        mock_sandbox.execute_shell_command.return_value = (1, "Some output", "Error occurred")

        success, output, error = commander_instance.execute(ast)

        assert success is False
        assert output == "Some output"
        assert error == "Error occurred"
        mock_sandbox.execute_shell_command.assert_called_once_with(expected_command)

    def test_execute_missing_command_template(self, commander_instance: Commander):
        ast = {
            "parameters": {"message": "Hello"},
            "action_type": "execute_command",
            # Missing "command_template"
        }
        success, output, error = commander_instance.execute(ast)
        assert success is False
        assert error == "Internal error: Command template missing in AST."

    def test_execute_unsupported_action_type(self, commander_instance: Commander):
        ast = {"command_template": "do_something", "parameters": {}, "action_type": "unknown_action"}
        success, output, error = commander_instance.execute(ast)
        assert success is False
        assert error == "Unsupported action type: unknown_action"

    def test_execute_command_rendering_key_error(self, commander_instance: Commander):
        """Test when command_template expects a parameter not in ast['parameters']"""
        ast = {
            "command_template": "echo {message} from {sender}",  # {sender} is missing
            "parameters": {"message": "Hello"},
            "action_type": "execute_command",
        }
        success, output, error = commander_instance.execute(ast)
        assert success is False
        assert "Error rendering command: Missing parameter 'sender'." in error

    def test_execute_sandbox_execution_error(self, commander_instance: Commander, mock_sandbox: MagicMock):
        ast = {"command_template": "dangerous_cmd", "parameters": {}, "action_type": "execute_command"}
        mock_sandbox.execute_shell_command.side_effect = SandboxExecutionError("Permission denied by sandbox")

        success, output, error = commander_instance.execute(ast)
        assert success is False
        assert error == "Permission denied by sandbox"

    def test_execute_unexpected_error_during_execution(self, commander_instance: Commander, mock_sandbox: MagicMock):
        ast = {"command_template": "cmd", "parameters": {}, "action_type": "execute_command"}
        # Simulate an unexpected error from sandbox or command rendering (other than KeyError)
        mock_sandbox.execute_shell_command.side_effect = ValueError("Unexpected sandbox problem")

        success, output, error = commander_instance.execute(ast)
        assert success is False
        assert "Unexpected error: Unexpected sandbox problem" in error

    # TODO: Add tests for other action_types like 'api_call' when implemented.
    # TODO: Test interaction with config if Commander uses any specific config values.
