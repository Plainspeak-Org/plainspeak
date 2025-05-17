"""
Learning System for PlainSpeak.

This module implements the feedback loop for improving command generation over time.
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import logging

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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    generated_command TEXT NOT NULL,
                    final_command TEXT,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    execution_time REAL NOT NULL,
                    feedback_type TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT
                )
            """
            )

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

    def record_feedback(
        self, entry: FeedbackEntry, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record feedback for a command generation.

        Args:
            entry: The feedback entry to record.
            metadata: Optional metadata about the feedback (e.g., user info, context).
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO feedback (
                    original_text,
                    generated_command,
                    final_command,
                    success,
                    error_message,
                    execution_time,
                    feedback_type,
                    timestamp,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.original_text,
                    entry.generated_command,
                    entry.final_command,
                    entry.success,
                    entry.error_message,
                    entry.execution_time,
                    entry.feedback_type,
                    entry.timestamp.isoformat(),
                    json.dumps(metadata) if metadata else None,
                ),
            )

    def analyze_patterns(self, min_occurrences: int = 5) -> pd.DataFrame:
        """
        Analyze feedback data to detect command patterns.

        Args:
            min_occurrences: Minimum number of occurrences for a pattern.

        Returns:
            DataFrame with pattern analysis results.
        """
        with sqlite3.connect(self.db_path) as conn:
            # Load feedback data into pandas
            df = pd.read_sql_query("SELECT * FROM feedback WHERE success = 1", conn)

            # Group by original text patterns
            patterns = (
                df.groupby("original_text")
                .agg(
                    {
                        "generated_command": "first",
                        "success": "count",
                        "execution_time": "mean",
                    }
                )
                .reset_index()
            )

            # Filter by minimum occurrences
            patterns = patterns[patterns["success"] >= min_occurrences]

            # Calculate success rate
            patterns["success_rate"] = patterns["success"] / patterns.groupby(
                "original_text"
            )["success"].transform("count")

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

    def get_training_data(
        self, min_success_rate: float = 0.8, limit: Optional[int] = None
    ) -> List[Tuple[str, str]]:
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

    def get_similar_examples(
        self, text: str, limit: int = 5
    ) -> List[Tuple[str, str, float]]:
        """
        Find similar examples from historical data.

        Args:
            text: The input text to find examples for.
            limit: Maximum number of examples to return.

        Returns:
            List of (original_text, command, success_rate) tuples.
        """
        patterns = pd.read_sql_query(
            "SELECT * FROM patterns", sqlite3.connect(self.db_path)
        )

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
