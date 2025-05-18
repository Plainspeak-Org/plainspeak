"""
Tests for the learning module.
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from plainspeak.learning import LearningStore


@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


def test_learning_store_init(temp_db_path):
    """Test LearningStore initialization and database creation."""
    LearningStore(temp_db_path)

    # Check that the database file was created
    assert temp_db_path.exists()

    # Check that the tables were created
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    assert "commands" in tables
    assert "feedback" in tables
    assert "patterns" in tables

    conn.close()


def test_add_command(temp_db_path):
    """Test adding a command to the learning store."""
    store = LearningStore(temp_db_path)

    # Add a command
    command_id = store.add_command(
        natural_text="list files",
        generated_command="ls -la",
        executed=True,
        success=True,
    )

    # Check that the command was added
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT natural_text, generated_command, executed, success FROM commands WHERE id = ?",
        (command_id,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "list files"
    assert row[1] == "ls -la"
    assert row[2] == 1  # executed = True
    assert row[3] == 1  # success = True


def test_update_command_execution(temp_db_path):
    """Test updating a command's execution status."""
    store = LearningStore(temp_db_path)

    # Add a command
    command_id = store.add_command(
        natural_text="list files",
        generated_command="ls -la",
        executed=False,
        success=None,
    )

    # Update execution status
    store.update_command_execution(command_id, True, True)

    # Check that the status was updated
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT executed, success FROM commands WHERE id = ?", (command_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == 1  # executed = True
    assert row[1] == 1  # success = True


def test_update_command_edit(temp_db_path):
    """Test updating a command with user edits."""
    store = LearningStore(temp_db_path)

    # Add a command
    command_id = store.add_command(natural_text="list files", generated_command="ls", executed=False)

    # Update with edit
    store.update_command_edit(command_id, "ls -la")

    # Check that the edit was saved
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT edited, edited_command FROM commands WHERE id = ?", (command_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == 1  # edited = True
    assert row[1] == "ls -la"


def test_add_feedback(temp_db_path):
    """Test adding feedback for a command."""
    store = LearningStore(temp_db_path)

    # Add a command
    command_id = store.add_command(natural_text="list files", generated_command="ls -la")

    # Add feedback
    store.add_feedback(command_id, "approve", "Great command!")

    # Check that the feedback was added
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT feedback_type, feedback_text FROM feedback WHERE command_id = ?",
        (command_id,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "approve"
    assert row[1] == "Great command!"


def test_get_command_history(temp_db_path):
    """Test getting command history."""
    store = LearningStore(temp_db_path)

    # Add multiple commands
    for i in range(5):
        store.add_command(
            natural_text=f"command {i}",
            generated_command=f"cmd{i}",
            executed=True,
            success=True,
        )

    # Get history
    history = store.get_command_history(limit=3)

    # Check that it's a DataFrame with the right structure
    assert isinstance(history, pd.DataFrame)
    assert len(history) == 3  # Limited to 3
    assert "natural_text" in history.columns
    assert "generated_command" in history.columns
    assert "executed" in history.columns
    assert "success" in history.columns


def test_get_command_with_feedback(temp_db_path):
    """Test getting a command with its feedback."""
    store = LearningStore(temp_db_path)

    # Add a command with system and environment info
    system_info = {"os": "test_os", "version": "1.0"}
    env_info = {"cwd": "/test", "shell": "bash"}

    command_id = store.add_command(
        natural_text="list files",
        generated_command="ls -la",
        executed=True,
        success=True,
        system_info=system_info,
        environment_info=env_info,
    )

    # Add feedback
    store.add_feedback(command_id, "approve", "Great!")
    store.add_feedback(command_id, "comment", "Very useful")

    # Get command with feedback
    command_data, feedback_list = store.get_command_with_feedback(command_id)

    # Check command data
    assert command_data["natural_text"] == "list files"
    assert command_data["generated_command"] == "ls -la"
    assert command_data["executed"] == 1
    assert command_data["success"] == 1
    assert command_data["system_info"] == system_info
    assert command_data["environment_info"] == env_info

    # Check feedback
    assert len(feedback_list) == 2
    assert feedback_list[0]["feedback_type"] == "approve"
    assert feedback_list[0]["feedback_text"] == "Great!"
    assert feedback_list[1]["feedback_type"] == "comment"
    assert feedback_list[1]["feedback_text"] == "Very useful"


def test_export_training_data(temp_db_path):
    """Test exporting training data."""
    store = LearningStore(temp_db_path)

    # Add some successful commands
    store.add_command(
        natural_text="list files",
        generated_command="ls -la",
        executed=True,
        success=True,
    )

    # Add an edited command
    command_id = store.add_command(natural_text="show hidden files", generated_command="ls", executed=False)
    store.update_command_edit(command_id, "ls -a")
    store.update_command_execution(command_id, True, True)

    # Add a failed command (shouldn't be exported)
    store.add_command(
        natural_text="invalid command",
        generated_command="invalid",
        executed=True,
        success=False,
    )

    # Export training data
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as f:
        output_path = Path(f.name)

    try:
        count = store.export_training_data(output_path)

        # Check that the right number of examples was exported
        assert count == 2

        # Check the file content
        with open(output_path, "r") as f:
            lines = f.readlines()

        assert len(lines) == 2

        # Parse the JSON lines
        examples = [json.loads(line) for line in lines]

        # Check the examples
        assert any(ex["input"] == "list files" and ex["output"] == "ls -la" for ex in examples)
        assert any(ex["input"] == "show hidden files" and ex["output"] == "ls -a" for ex in examples)

    finally:
        # Cleanup
        if output_path.exists():
            output_path.unlink()
