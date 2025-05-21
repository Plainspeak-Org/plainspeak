"""
Learning System for PlainSpeak.

This module implements the feedback loop for improving command generation over time.
Uses JSON-based storage for flexibility and simplicity.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Command generation entry."""

    id: str  # UUID
    natural_text: str
    generated_command: str
    edited: bool = False
    edited_command: Optional[str] = None
    executed: bool = False
    success: Optional[bool] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = ""  # ISO format
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Feedback:
    """Feedback for a command."""

    command_id: str
    feedback_type: str  # 'approve', 'edit', 'reject'
    feedback_text: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Pattern:
    """Usage pattern detected from commands."""

    pattern: str
    command_template: str
    success_rate: float
    usage_count: int
    last_used: str  # ISO format
    metadata: Optional[Dict[str, Any]] = None


class LearningStore:
    """
    Store for collecting and analyzing command generation feedback.
    Uses JSON files for flexible storage without schema constraints.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the learning store.

        Args:
            data_dir: Directory for JSON storage. If None, uses ~/.plainspeak/learning/
        """
        if data_dir is None:
            data_dir = Path.home() / ".plainspeak" / "learning"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize storage files
        self.commands_file = self.data_dir / "commands.json"
        self.feedback_file = self.data_dir / "feedback.json"
        self.patterns_file = self.data_dir / "patterns.json"

        self._init_storage()

    def _init_storage(self) -> None:
        """Initialize JSON storage files if they don't exist."""
        for file in [self.commands_file, self.feedback_file, self.patterns_file]:
            if not file.exists():
                file.write_text("[]")

    def _load_json(self, file: Path) -> List[Dict[str, Any]]:
        """Load data from a JSON file."""
        try:
            return json.loads(file.read_text())
        except json.JSONDecodeError:
            logger.error(f"Error reading {file}, returning empty list")
            return []

    def _save_json(self, file: Path, data: List[Dict[str, Any]]) -> None:
        """Save data to a JSON file."""
        file.write_text(json.dumps(data, indent=2))

    def add_command(
        self,
        natural_text: str,
        generated_command: str,
        executed: bool = False,
        success: Optional[bool] = None,
        system_info: Optional[Dict[str, Any]] = None,
        environment_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a command and return its ID."""
        import uuid

        command = Command(
            id=str(uuid.uuid4()),
            natural_text=natural_text,
            generated_command=generated_command,
            executed=executed,
            success=success,
            metadata={"system_info": system_info or {}, "environment_info": environment_info or {}},
        )

        commands = self._load_json(self.commands_file)
        commands.append(asdict(command))
        self._save_json(self.commands_file, commands)

        return command.id

    def add_feedback(self, command_id: str, feedback_type: str, message: Optional[str] = None) -> None:
        """Add feedback for a command."""
        feedback = Feedback(command_id=command_id, feedback_type=feedback_type, feedback_text=message)

        feedbacks = self._load_json(self.feedback_file)
        feedbacks.append(asdict(feedback))
        self._save_json(self.feedback_file, feedbacks)

    def update_command_execution(
        self, command_id: str, executed: bool, success: bool, error_message: Optional[str] = None
    ) -> None:
        """Update command execution results."""
        commands = self._load_json(self.commands_file)

        for cmd in commands:
            if cmd["id"] == command_id:
                cmd["executed"] = executed
                cmd["success"] = success
                if error_message:
                    cmd["error_message"] = error_message
                break

        self._save_json(self.commands_file, commands)

    def update_command_edit(self, command_id: str, edited_command: str) -> None:
        """Update command with user edits."""
        commands = self._load_json(self.commands_file)

        for cmd in commands:
            if cmd["id"] == command_id:
                cmd["edited"] = True
                cmd["edited_command"] = edited_command
                break

        self._save_json(self.commands_file, commands)

    def get_command_history(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Get command history as a DataFrame."""
        commands = self._load_json(self.commands_file)
        df = pd.DataFrame(commands)

        if df.empty:
            return df

        df = df.sort_values("timestamp", ascending=False)
        return df.head(limit) if limit else df

    def get_training_data(self, min_success_rate: float = 0.8, limit: Optional[int] = None) -> List[Tuple[str, str]]:
        """Get successful commands for training."""
        commands = self._load_json(self.commands_file)
        results: List[Tuple[str, str]] = []

        for cmd in commands:
            if cmd.get("success") and cmd.get("executed"):
                command = cmd.get("edited_command") if cmd.get("edited") else cmd["generated_command"]
                results.append((cmd["natural_text"], command))

        if limit:
            results = results[:limit]

        return results

    def get_similar_examples(self, text: str, limit: int = 5) -> List[Tuple[str, str, float]]:
        """Find similar examples from history."""
        commands = self._load_json(self.commands_file)
        text_words = set(text.lower().split())
        results: List[Tuple[str, str, float]] = []

        for cmd in commands:
            if cmd.get("success"):
                pattern_words = set(cmd["natural_text"].lower().split())
                common_words = text_words & pattern_words
                if common_words:
                    score = len(common_words) / max(len(text_words), len(pattern_words))
                    command = cmd.get("edited_command") if cmd.get("edited") else cmd["generated_command"]
                    results.append((cmd["natural_text"], command, score))

        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    def export_training_data(self, output_path: Path) -> int:
        """Export training data to JSONL."""
        successful_commands = [
            cmd for cmd in self._load_json(self.commands_file) if cmd.get("success") and cmd.get("executed")
        ]

        if not successful_commands:
            return 0

        with open(output_path, "w") as f:
            for cmd in successful_commands:
                command = cmd.get("edited_command") if cmd.get("edited") else cmd["generated_command"]
                f.write(
                    json.dumps(
                        {
                            "input": cmd["natural_text"],
                            "output": command,
                        }
                    )
                    + "\n"
                )

        return len(successful_commands)


# Global learning store instance
learning_store = LearningStore()
