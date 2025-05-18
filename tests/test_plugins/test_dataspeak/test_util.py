"""
Tests for the Utility module of the DataSpeak plugin.
"""

import json
from unittest.mock import patch

import pandas as pd
import pytest

from plainspeak.plugins.dataspeak.util import (
    chunk_long_results,
    format_error,
    format_value_for_display,
    get_column_display_width,
    parse_json_params,
    results_to_csv,
    results_to_json,
    results_to_table,
    sanitize_output,
    summarize_results,
)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
            "age": [25, 30, 35, 40, 45],
            "active": [True, False, True, True, False],
        }
    )


@pytest.fixture
def sample_records():
    """Create a sample list of records for testing."""
    return [
        {"id": 1, "name": "Alice", "age": 25, "active": True},
        {"id": 2, "name": "Bob", "age": 30, "active": False},
        {"id": 3, "name": "Charlie", "age": 35, "active": True},
        {"id": 4, "name": "David", "age": 40, "active": True},
        {"id": 5, "name": "Eve", "age": 45, "active": False},
    ]


class TestFormattingFunctions:
    """Tests for result formatting functions."""

    def test_results_to_table_dataframe(self, sample_dataframe):
        """Test formatting DataFrame as table."""
        # With tabulate available
        with patch("plainspeak.plugins.dataspeak.util.HAS_TABULATE", True):
            with patch("plainspeak.plugins.dataspeak.util.tabulate") as mock_tabulate:
                mock_tabulate.return_value = "Mocked Table Output"
                result = results_to_table(sample_dataframe)
                assert result == "Mocked Table Output"
                mock_tabulate.assert_called_once()

        # Without tabulate (fallback to pandas)
        with patch("plainspeak.plugins.dataspeak.util.HAS_TABULATE", False):
            result = results_to_table(sample_dataframe)
            assert isinstance(result, str)
            assert "id" in result
            assert "name" in result
            assert "Alice" in result

    def test_results_to_table_records(self, sample_records):
        """Test formatting records list as table."""
        # With tabulate available
        with patch("plainspeak.plugins.dataspeak.util.HAS_TABULATE", True):
            with patch("plainspeak.plugins.dataspeak.util.tabulate") as mock_tabulate:
                mock_tabulate.return_value = "Mocked Table Output"
                result = results_to_table(sample_records)
                assert result == "Mocked Table Output"
                mock_tabulate.assert_called_once()

        # Without tabulate (fallback to pandas)
        with patch("plainspeak.plugins.dataspeak.util.HAS_TABULATE", False):
            result = results_to_table(sample_records)
            assert isinstance(result, str)
            assert "id" in result
            assert "name" in result
            assert "Alice" in result

    def test_results_to_table_empty(self):
        """Test formatting empty results."""
        result = results_to_table([])
        assert result == "No results found."

        result = results_to_table(pd.DataFrame())
        assert result == "No results found."

    def test_results_to_json_dataframe(self, sample_dataframe):
        """Test formatting DataFrame as JSON."""
        result = results_to_json(sample_dataframe)
        assert isinstance(result, str)

        # Verify JSON is valid and contains correct data
        data = json.loads(result)
        assert len(data) == 5
        assert data[0]["name"] == "Alice"
        assert data[1]["age"] == 30

    def test_results_to_json_records(self, sample_records):
        """Test formatting records list as JSON."""
        result = results_to_json(sample_records)
        assert isinstance(result, str)

        # Verify JSON is valid and contains correct data
        data = json.loads(result)
        assert len(data) == 5
        assert data[0]["name"] == "Alice"
        assert data[1]["age"] == 30

    def test_results_to_json_error_handling(self):
        """Test error handling in JSON formatting."""

        # Create a DataFrame with non-serializable objects
        class NonSerializable:
            pass

        df = pd.DataFrame({"obj": [NonSerializable()]})

        # Should not raise exception, but return empty JSON
        result = results_to_json(df)
        assert result == "{}"

    def test_results_to_csv_dataframe(self, sample_dataframe):
        """Test formatting DataFrame as CSV."""
        result = results_to_csv(sample_dataframe)
        assert isinstance(result, str)

        # Verify CSV contains headers and data
        lines = result.strip().split("\n")
        assert len(lines) == 6  # header + 5 rows
        assert "id,name,age,active" in lines[0]
        assert "1,Alice,25,True" in lines[1]

    def test_results_to_csv_records(self, sample_records):
        """Test formatting records list as CSV."""
        result = results_to_csv(sample_records)
        assert isinstance(result, str)

        # Verify CSV contains headers and data
        lines = result.strip().split("\n")
        assert len(lines) == 6  # header + 5 rows
        assert "id,name,age,active" in lines[0]
        assert "1,Alice,25,True" in lines[1]

    def test_results_to_csv_empty(self):
        """Test formatting empty results as CSV."""
        result = results_to_csv([])
        assert result == ""

        result = results_to_csv(pd.DataFrame())
        assert result == ""

    def test_results_to_csv_no_header(self, sample_dataframe):
        """Test formatting CSV without headers."""
        result = results_to_csv(sample_dataframe, include_header=False)
        assert isinstance(result, str)

        # Verify CSV contains only data (no header)
        lines = result.strip().split("\n")
        assert len(lines) == 5  # 5 rows, no header
        assert "1,Alice,25,True" in lines[0]


class TestUtilityFunctions:
    """Tests for utility helper functions."""

    def test_parse_json_params(self):
        """Test JSON parameter parsing."""
        # Valid JSON
        params = parse_json_params('{"name": "test", "value": 123}')
        assert params == {"name": "test", "value": 123}

        # Invalid JSON
        with pytest.raises(ValueError):
            parse_json_params("{name: test}")

    def test_format_error(self):
        """Test error formatting."""
        # Basic error
        result = format_error("Something went wrong")
        assert result == "Error: Something went wrong"

        # Custom error type
        result = format_error("Access denied", error_type="Security Error")
        assert result == "Security Error: Access denied"

    def test_sanitize_output(self):
        """Test output sanitization and truncation."""
        # Short output (no truncation)
        short_output = "This is a short output"
        result = sanitize_output(short_output)
        assert result == short_output

        # Long output (truncation)
        long_output = "a" * 3000
        result = sanitize_output(long_output)
        assert len(result) < len(long_output)
        assert "..." in result
        assert "truncated" in result

        # Custom max length
        result = sanitize_output("abcdefghij", max_length=5)
        assert len(result) < 10
        assert "..." in result
        assert "truncated" in result

    def test_get_column_display_width(self, sample_dataframe):
        """Test column width calculation."""
        # Text column
        width = get_column_display_width(sample_dataframe, "name")
        # Width should include the column name length and the longest value plus padding
        assert width >= len("Charlie") + 2

        # Numeric column
        width = get_column_display_width(sample_dataframe, "age")
        # Width should include the column name length and space for the values plus padding
        assert width >= len("age") + 2

    def test_format_value_for_display(self):
        """Test value formatting for display."""
        # None value
        assert format_value_for_display(None) == "NULL"

        # Float value
        assert format_value_for_display(123.456789) == "123.457"

        # List value
        assert format_value_for_display([1, 2, 3]) == "[1, 2, 3]"

        # Dict value
        assert format_value_for_display({"key": "value"}) == '{"key": "value"}'

        # String value
        assert format_value_for_display("test") == "test"

    def test_chunk_long_results(self, sample_records):
        """Test chunking of long result sets."""
        # No chunking needed (results smaller than chunk size)
        chunks = chunk_long_results(sample_records, max_rows_per_chunk=10)
        assert len(chunks) == 1
        assert len(chunks[0]) == 5

        # Chunking needed
        chunks = chunk_long_results(sample_records, max_rows_per_chunk=2)
        assert len(chunks) == 3
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 2
        assert len(chunks[2]) == 1

    def test_summarize_results_dataframe(self, sample_dataframe):
        """Test result summarization with DataFrame."""
        summary = summarize_results(sample_dataframe)

        # Check basic summary stats
        assert summary["row_count"] == 5
        assert summary["column_count"] == 4
        assert "id" in summary["columns"]
        assert "name" in summary["columns"]

        # Check numeric column stats
        assert "id" in summary["numeric_columns"]
        assert "age" in summary["numeric_columns"]
        assert "name" not in summary["numeric_columns"]

        # Check detailed stats
        assert summary["stats"]["age"]["min"] == 25
        assert summary["stats"]["age"]["max"] == 45
        assert summary["stats"]["age"]["mean"] == 35

    def test_summarize_results_records(self, sample_records):
        """Test result summarization with records list."""
        summary = summarize_results(sample_records)

        # Check basic summary stats
        assert summary["row_count"] == 5
        assert summary["column_count"] == 4
        assert "id" in summary["columns"]
        assert "name" in summary["columns"]

        # Check numeric column stats
        assert "id" in summary["numeric_columns"]
        assert "age" in summary["numeric_columns"]
        assert "name" not in summary["numeric_columns"]

        # Check detailed stats
        assert summary["stats"]["age"]["min"] == 25
        assert summary["stats"]["age"]["max"] == 45
        assert summary["stats"]["age"]["mean"] == 35

    def test_summarize_results_empty(self):
        """Test summarization of empty results."""
        summary = summarize_results([])
        assert summary["row_count"] == 0
        assert summary["column_count"] == 0
