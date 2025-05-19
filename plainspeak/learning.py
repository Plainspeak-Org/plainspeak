"""
Learning System for PlainSpeak.

This module implements the feedback loop for improving command generation over time.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Feedback data for a command generation."""

    original_text: str
    generated_command: str
    final_command: Optional[str]
    success: bool
    error_message: Optional[str]
    execution_time: float
    feedback_type: str  # 'accept', 'edit', 'reject'
    timestamp: datetime


class LearningStore:
    """
    Store for collecting and analyzing command generation feedback.

    Features:
    - SQLite storage for feedback data
    - Pandas analysis for pattern detection
    - Feedback queuing for model fine-tuning
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the learning store.

        Args:
            db_path: Path to SQLite database file. If None, uses ~/.plainspeak/learning.db
        """
        if db_path is None:
            db_path = Path.home() / ".plainspeak" / "learning.db"

        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Create the commands table for test compatibility
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    natural_text TEXT NOT NULL,
                    generated_command TEXT NOT NULL,
                    edited BOOLEAN DEFAULT 0,
                    edited_command TEXT,
                    executed BOOLEAN DEFAULT 0,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time REAL DEFAULT 0.0,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            """
            )

            # Create the feedback table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id INTEGER NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_text TEXT,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (command_id) REFERENCES commands(id)
                )
            """
            )

            # Create the patterns table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    command_template TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    usage_count INTEGER NOT NULL,
                    last_used DATETIME NOT NULL,
                    metadata TEXT
                )
            """
            )

    def record_feedback(self, entry: FeedbackEntry, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record feedback for a command generation.

        Args:
            entry: The feedback entry to record.
            metadata: Optional metadata about the feedback (e.g., user info, context).
        """
        # First add the command
        command_id = self.add_command(
            natural_text=entry.original_text,
            generated_command=entry.generated_command,
            executed=entry.success is not None,
            success=entry.success,
        )

        # Then add the feedback
        self.add_feedback(
            command_id=command_id,
            feedback_type=entry.feedback_type,
            message=entry.error_message,
        )

    def add_command(
        self,
        natural_text: str,
        generated_command: str,
        executed: bool = False,
        success: Optional[bool] = None,
        system_info: Optional[Dict[str, Any]] = None,
        environment_info: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add a command to the learning store.

        Args:
            natural_text: The original natural language text.
            generated_command: The generated command.
            executed: Whether the command was executed.
            success: Whether the command execution was successful.
            system_info: System information.
            environment_info: Environment information.

        Returns:
            The ID of the added command.

        Raises:
            sqlite3.Error: If there is a database error.
        """
        metadata = json.dumps(
            {
                "system_info": system_info or {},
                "environment_info": environment_info or {},
            }
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO commands (
                    natural_text,
                    generated_command,
                    executed,
                    success,
                    execution_time,
                    timestamp,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    natural_text,
                    generated_command,
                    1 if executed else 0,  # SQLite uses 1/0 for booleans
                    1 if success else (0 if success is False else None),  # Handle None case
                    0.0,  # execution time is 0 until measured
                    datetime.now().isoformat(),
                    metadata,
                ),
            )
            # lastrowid is guaranteed to be an integer when INSERT is successful
            return cursor.lastrowid or 0  # Return 0 if for some reason lastrowid is None

    def add_feedback(self, command_id: int, feedback_type: str, message: Optional[str] = None) -> None:
        """
        Add feedback for a command.

        Args:
            command_id: The ID of the command.
            feedback_type: The type of feedback ('approve', 'reject', etc.).
            message: Optional message associated with the feedback.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Insert a new feedback entry
            conn.execute(
                """
                INSERT INTO feedback (
                    command_id,
                    feedback_type,
                    feedback_text,
                    timestamp
                ) VALUES (?, ?, ?, ?)
                """,
                (command_id, feedback_type, message, datetime.now().isoformat()),
            )

    def update_command_execution(
        self,
        command_id: int,
        executed: bool,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Update a command with execution results.

        Args:
            command_id: The ID of the command.
            executed: Whether the command was executed.
            success: Whether the command execution was successful.
            error_message: Optional error message if execution failed.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE commands
                SET executed = ?,
                    success = ?,
                    error_message = ?
                WHERE id = ?
                """,
                (1 if executed else 0, 1 if success else 0, error_message, command_id),
            )

    def update_command_edit(self, command_id: int, edited_command: str) -> None:
        """
        Update a command with user edits.

        Args:
            command_id: The ID of the command.
            edited_command: The edited command.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE commands
                SET edited = ?,
                    edited_command = ?
                WHERE id = ?
                """,
                (1, edited_command, command_id),
            )

    def get_command_history(self, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Get the command history from the commands table.

        Args:
            limit: Optional limit on the number of records to return.

        Returns:
            DataFrame with command history.
        """
        query = "SELECT * FROM commands ORDER BY timestamp DESC"
        if limit is not None:
            query += f" LIMIT {limit}"

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn)

    def get_command_with_feedback(self, command_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get a command with its feedback.

        Args:
            command_id: The ID of the command.

        Returns:
            Tuple of (command_data, feedback_list).
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get command data
            cursor = conn.execute("SELECT * FROM commands WHERE id = ?", (command_id,))
            command_row = cursor.fetchone()

            if not command_row:
                return {}, []

            # Convert to dict
            columns = [col[0] for col in cursor.description]
            command_data = dict(zip(columns, command_row))

            # Parse metadata
            if command_data.get("metadata"):
                metadata = json.loads(command_data["metadata"])
                command_data["system_info"] = metadata.get("system_info", {})
                command_data["environment_info"] = metadata.get("environment_info", {})

            # Get feedback
            cursor = conn.execute("SELECT * FROM feedback WHERE command_id = ?", (command_id,))
            feedback_rows = cursor.fetchall()

            # Convert to list of dicts
            columns = [col[0] for col in cursor.description]
            feedback_list = [dict(zip(columns, row)) for row in feedback_rows]

            return command_data, feedback_list

    def export_training_data(self, output_path: Path) -> int:
        """
        Export training data to a JSONL file.

        Args:
            output_path: Path to the output file.

        Returns:
            Number of records exported.
        """
        # Get successful commands with high-quality feedback
        df = self.get_command_history()

        # Filter for successful commands
        df = df[(df["success"] == 1) & (df["executed"] == 1)]  # SQLite stores booleans as 1/0

        if df.empty:
            return 0

        # Write to JSONL file
        with open(output_path, "w") as f:
            for _, row in df.iterrows():
                # Use edited command if available
                command = (
                    row["edited_command"] if row["edited"] == 1 and row["edited_command"] else row["generated_command"]
                )

                f.write(
                    json.dumps(
                        {
                            "input": row["natural_text"],
                            "output": command,
                        }
                    )
                    + "\n"
                )

        return len(df)

    def analyze_patterns(self, min_occurrences: int = 5) -> pd.DataFrame:
        """
        Analyze feedback data to detect command patterns.

        Args:
            min_occurrences: Minimum number of occurrences for a pattern.

        Returns:
            DataFrame with pattern analysis results.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Load command data into pandas
            df = pd.read_sql_query("SELECT * FROM commands WHERE success = 1", conn)

            if df.empty:
                # Return empty DataFrame with expected columns
                return pd.DataFrame(
                    columns=["pattern", "command_template", "success_count", "execution_time", "success_rate"]
                )

            # Group by natural text patterns
            patterns = (
                df.groupby("natural_text")
                .agg(
                    {
                        "generated_command": "first",
                        "id": "count",  # Count as success_count
                        "execution_time": "mean",
                    }
                )
                .reset_index()
            )

            # Rename columns for clarity
            patterns = patterns.rename(
                columns={"natural_text": "pattern", "generated_command": "command_template", "id": "success_count"}
            )

            # Filter by minimum occurrences
            patterns = patterns[patterns["success_count"] >= min_occurrences]

            # Calculate success rate (all are successful in this query)
            patterns["success_rate"] = 1.0

            return patterns

    def update_patterns(self) -> None:
        """Update the patterns table with new analysis results."""
        patterns = self.analyze_patterns()

        with sqlite3.connect(self.db_path) as conn:
            # Clear old patterns
            conn.execute("DELETE FROM patterns")

            # Insert new patterns
            for _, row in patterns.iterrows():
                conn.execute(
                    """
                    INSERT INTO patterns (
                        pattern,
                        command_template,
                        success_rate,
                        usage_count,
                        last_used,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["original_text"],
                        row["generated_command"],
                        row["success_rate"],
                        int(row["success"]),
                        datetime.now().isoformat(),
                        None,
                    ),
                )

    def get_training_data(self, min_success_rate: float = 0.8, limit: Optional[int] = None) -> List[Tuple[str, str]]:
        """
        Get successful command generations for model fine-tuning.

        Args:
            min_success_rate: Minimum success rate to include a pattern.
            limit: Maximum number of examples to return.

        Returns:
            List of (original_text, command) tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT pattern, command_template
                FROM patterns
                WHERE success_rate >= ?
                ORDER BY usage_count DESC
            """

            if limit is not None:
                query += f" LIMIT {limit}"

            cursor = conn.execute(query, (min_success_rate,))
            return cursor.fetchall()

    def get_similar_examples(self, text: str, limit: int = 5) -> List[Tuple[str, str, float]]:
        """
        Find similar examples from historical data.

        Args:
            text: The input text to find examples for.
            limit: Maximum number of examples to return.

        Returns:
            List of (original_text, command, success_rate) tuples.
        """
        patterns = pd.read_sql_query("SELECT * FROM patterns", sqlite3.connect(self.db_path))

        # TODO: Implement proper similarity scoring
        # For now, just check if text contains any pattern words
        text_words = set(text.lower().split())

        results = []
        for _, row in patterns.iterrows():
            pattern_words = set(row["pattern"].lower().split())
            common_words = text_words & pattern_words
            if common_words:
                score = len(common_words) / max(len(text_words), len(pattern_words))
                results.append((row["pattern"], row["command_template"], score))

        # Sort by score and limit results
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]


# Global learning store instance
learning_store = LearningStore()
