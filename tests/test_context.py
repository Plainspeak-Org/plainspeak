"""
Tests for the context module.
"""

import json
import tempfile
from pathlib import Path

import pytest

from plainspeak.context import SessionContext


@pytest.fixture
def temp_context_file():
    """Create a temporary file for context storage."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


def test_session_context_init():
    """Test SessionContext initialization."""
    context = SessionContext()
    assert context._session_vars == {}
    assert context._command_history == []


def test_session_context_system_info():
    """Test getting system information."""
    context = SessionContext()
    system_info = context.get_system_info()

    # Check that essential keys are present
    assert "os" in system_info
    assert "hostname" in system_info
    assert "username" in system_info
    assert "python_version" in system_info


def test_session_context_environment_info():
    """Test getting environment information."""
    context = SessionContext()
    env_info = context.get_environment_info()

    # Check that essential keys are present
    assert "cwd" in env_info
    assert "home" in env_info
    assert "shell" in env_info
    assert "path" in env_info


def test_session_context_add_to_history():
    """Test adding commands to history."""
    context = SessionContext()

    # Add a command
    context.add_to_history("list files", "ls -la", True)

    # Check that it was added
    history = context.get_history()
    assert len(history) == 1
    assert history[0]["natural_text"] == "list files"
    assert history[0]["command"] == "ls -la"
    assert history[0]["success"] is True
    assert "timestamp" in history[0]


def test_session_context_get_history_limit():
    """Test getting history with a limit."""
    context = SessionContext()

    # Add multiple commands
    for i in range(5):
        context.add_to_history(f"command {i}", f"cmd{i}", True)

    # Get limited history
    history = context.get_history(limit=3)
    assert len(history) == 3
    # Most recent should be first
    assert history[0]["natural_text"] == "command 4"
    assert history[1]["natural_text"] == "command 3"
    assert history[2]["natural_text"] == "command 2"


def test_session_context_session_vars():
    """Test setting and getting session variables."""
    context = SessionContext()

    # Set a variable
    context.set_session_var("test_key", "test_value")

    # Get the variable
    assert context.get_session_var("test_key") == "test_value"

    # Get a non-existent variable with default
    assert context.get_session_var("non_existent", "default") == "default"

    # Get all variables
    all_vars = context.get_all_session_vars()
    assert "test_key" in all_vars
    assert all_vars["test_key"] == "test_value"


def test_session_context_save_load(temp_context_file):
    """Test saving and loading context."""
    # Create context with a file
    context = SessionContext(temp_context_file)

    # Add data
    context.set_session_var("test_key", "test_value")
    context.add_to_history("test command", "test_cmd", True)

    # Save
    context.save_context()

    # Check that file exists and contains expected data
    assert temp_context_file.exists()
    with open(temp_context_file, "r") as f:
        data = json.load(f)
        assert "session_vars" in data
        assert "command_history" in data
        assert data["session_vars"]["test_key"] == "test_value"
        assert len(data["command_history"]) == 1
        assert data["command_history"][0]["natural_text"] == "test command"

    # Create a new context with the same file
    new_context = SessionContext(temp_context_file)

    # Check that data was loaded
    assert new_context.get_session_var("test_key") == "test_value"
    history = new_context.get_history()
    assert len(history) == 1
    assert history[0]["natural_text"] == "test command"


def test_session_context_get_full_context():
    """Test getting the full context."""
    context = SessionContext()

    # Add some data
    context.set_session_var("test_key", "test_value")
    context.add_to_history("test command", "test_cmd", True)

    # Get full context
    full_context = context.get_full_context()

    # Check structure
    assert "system" in full_context
    assert "environment" in full_context
    assert "session_vars" in full_context
    assert "history_size" in full_context

    # Check content
    assert full_context["session_vars"]["test_key"] == "test_value"
    assert full_context["history_size"] == 1


def test_session_context_get_context_for_llm():
    """Test getting formatted context for LLM."""
    context = SessionContext()

    # Add some data
    context.set_session_var("test_key", "test_value")
    context.add_to_history("test command", "test_cmd", True)

    # Get context for LLM
    llm_context = context.get_context_for_llm()

    # Check that it's a non-empty string
    assert isinstance(llm_context, str)
    assert len(llm_context) > 0

    # Check that it contains key information
    assert "Operating System:" in llm_context
    assert "Current Directory:" in llm_context
    assert "Session Variables:" in llm_context
    assert "test_key: test_value" in llm_context
