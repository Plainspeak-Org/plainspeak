"""
Tests for the learning module.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from plainspeak.learning import LearningStore


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for JSON files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def test_learning_store_init(temp_data_dir):
    """Test LearningStore initialization and file creation."""
    LearningStore(temp_data_dir)

    # Check that JSON files were created
    assert (temp_data_dir / "commands.json").exists()
    assert (temp_data_dir / "feedback.json").exists()
    assert (temp_data_dir / "patterns.json").exists()

    # Check that files contain valid empty JSON arrays
    for filename in ["commands.json", "feedback.json", "patterns.json"]:
        content = (temp_data_dir / filename).read_text()
        assert json.loads(content) == []


def test_add_command(temp_data_dir):
    """Test adding a command to the learning store."""
    store = LearningStore(temp_data_dir)

    # Add a command
    command_id = store.add_command(
        natural_text="list files",
        generated_command="ls -la",
        executed=True,
        success=True,
    )

    # Check that the command was added
    commands = json.loads((temp_data_dir / "commands.json").read_text())
    assert len(commands) == 1
    cmd = commands[0]

    assert cmd["id"] == command_id
    assert cmd["natural_text"] == "list files"
    assert cmd["generated_command"] == "ls -la"
    assert cmd["executed"] is True
    assert cmd["success"] is True


def test_update_command_execution(temp_data_dir):
    """Test updating a command's execution status."""
    store = LearningStore(temp_data_dir)

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
    commands = json.loads((temp_data_dir / "commands.json").read_text())
    cmd = next(c for c in commands if c["id"] == command_id)

    assert cmd["executed"] is True
    assert cmd["success"] is True


def test_update_command_edit(temp_data_dir):
    """Test updating a command with user edits."""
    store = LearningStore(temp_data_dir)

    # Add a command
    command_id = store.add_command(natural_text="list files", generated_command="ls", executed=False)

    # Update with edit
    store.update_command_edit(command_id, "ls -la")

    # Check that the edit was saved
    commands = json.loads((temp_data_dir / "commands.json").read_text())
    cmd = next(c for c in commands if c["id"] == command_id)

    assert cmd["edited"] is True
    assert cmd["edited_command"] == "ls -la"


def test_add_feedback(temp_data_dir):
    """Test adding feedback for a command."""
    store = LearningStore(temp_data_dir)

    # Add a command
    command_id = store.add_command(natural_text="list files", generated_command="ls -la")

    # Add feedback
    store.add_feedback(command_id, "approve", "Great command!")

    # Check that the feedback was added
    feedbacks = json.loads((temp_data_dir / "feedback.json").read_text())
    assert len(feedbacks) == 1
    feedback = feedbacks[0]

    assert feedback["command_id"] == command_id
    assert feedback["feedback_type"] == "approve"
    assert feedback["feedback_text"] == "Great command!"


def test_get_command_history(temp_data_dir):
    """Test getting command history."""
    store = LearningStore(temp_data_dir)

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


def test_get_similar_examples(temp_data_dir):
    """Test finding similar examples."""
    store = LearningStore(temp_data_dir)

    # Add some test commands
    store.add_command(
        natural_text="list all files",
        generated_command="ls -la",
        executed=True,
        success=True,
    )
    store.add_command(
        natural_text="show hidden files",
        generated_command="ls -a",
        executed=True,
        success=True,
    )

    # Find similar examples
    examples = store.get_similar_examples("list hidden files", limit=2)

    assert len(examples) == 2
    # Should match both due to common words, with "list" command having higher score
    assert any(ex[0] == "list all files" for ex in examples)
    assert any(ex[0] == "show hidden files" for ex in examples)


def test_export_training_data(temp_data_dir):
    """Test exporting training data."""
    store = LearningStore(temp_data_dir)

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
