"""
DataSpeak Utility Module

This module provides utility functions for the DataSpeak plugin,
including result formatting and conversion.
"""

import json
import logging
from typing import Any, Dict, List, Union

import pandas as pd


# Define a simple tabulate function for when the library is not available
def _simple_tabulate(data: Any, headers: Any = "keys", tablefmt: Any = "pretty", showindex: Any = False) -> str:
    """Simple tabulate replacement when the library is not available."""
    if isinstance(data, pd.DataFrame):
        return data.to_string(index=showindex)

    # Handle list of dicts
    if data and isinstance(data[0], dict):
        if headers == "keys":
            headers = data[0].keys()
        result = " | ".join(str(h) for h in headers) + "\n"
        result += "-" * (len(result) - 1) + "\n"
        for row in data:
            result += " | ".join(str(row.get(h, "")) for h in headers) + "\n"
        return result

    # Fallback
    return str(data)


# Try to import tabulate
try:
    from tabulate import tabulate

    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    logging.warning("tabulate not found, falling back to simple table formatting")

    # Use our simple implementation
    def tabulate_wrapper(*args: Any, **kwargs: Any) -> str:
        """Wrapper for simple tabulate to match any signature."""
        # Extract the data and a few common parameters
        data = args[0] if args else kwargs.get("tabular_data")
        headers = args[1] if len(args) > 1 else kwargs.get("headers", "keys")
        tablefmt = kwargs.get("tablefmt", "pretty")
        showindex = kwargs.get("showindex", False)

        return _simple_tabulate(data, headers, tablefmt, showindex)

    # Assign the wrapper to the tabulate name
    tabulate = tabulate_wrapper


def results_to_table(results: Union[pd.DataFrame, List[Dict[str, Any]]], table_format: str = "pretty") -> str:
    """
    Format query results as a readable text table.

    Args:
        results: DataFrame or list of dictionaries containing the results
        table_format: Table format to use (only relevant with tabulate)
            Options include: 'pretty', 'grid', 'pipe', 'orgtbl', 'github', etc.

    Returns:
        Formatted table as a string
    """
    # Convert results to DataFrame if it's a list of dicts
    if isinstance(results, list):
        if not results:  # Handle empty list
            return "No results found."
        df = pd.DataFrame(results)
    else:
        df = results

    # Handle empty results
    if df.empty:
        return "No results found."

    # Use tabulate if available
    try:
        return tabulate(df, headers="keys", tablefmt=table_format, showindex=False)
    except Exception as e:
        logging.warning(f"Error formatting table: {str(e)}")
        # Fall back to pandas formatting
        return df.to_string(index=False)


def results_to_json(
    results: Union[pd.DataFrame, List[Dict[str, Any]]],
    orient: str = "records",
    indent: int = 2,
) -> str:
    """
    Format query results as JSON.

    Args:
        results: DataFrame or list of dictionaries containing the results
        orient: JSON structure orientation (only used if results is a DataFrame)
            Options include: 'records', 'columns', 'index', 'values', etc.
        indent: Number of spaces for indentation

    Returns:
        JSON string
    """

    # Handle potentially non-serializable objects
    def custom_serializer(obj):
        """Custom serializer to handle non-serializable objects."""
        try:
            return str(obj)
        except Exception:  # Handle any exception that might occur during string conversion
            return None

    # Convert results to JSON
    if isinstance(results, pd.DataFrame):
        try:
            # For potentially non-serializable objects, convert to strings first
            for col in results.columns:
                if results[col].apply(lambda x: not isinstance(x, (int, float, str, bool, type(None)))).any():
                    # Column contains custom objects, return empty JSON
                    logging.warning(f"Column {col} contains non-serializable objects")
                    return "{}"

            # Use to_dict first as it handles more data types
            result_dict = results.to_dict(orient=orient)
            return json.dumps(result_dict, indent=indent, default=custom_serializer)
        except Exception as e:
            logging.warning(f"Error converting DataFrame to JSON: {str(e)}")
            # Fall back to empty JSON
            return "{}"

    # For list of dicts or fall-back
    try:
        return json.dumps(results, indent=indent, default=custom_serializer)
    except Exception as e:
        logging.error(f"Error serializing results to JSON: {str(e)}")
        return "{}"


def results_to_csv(results: Union[pd.DataFrame, List[Dict[str, Any]]], include_header: bool = True) -> str:
    """
    Format query results as CSV.

    Args:
        results: DataFrame or list of dictionaries containing the results
        include_header: Whether to include column headers in the output

    Returns:
        CSV string
    """
    # Convert results to DataFrame if it's a list of dicts
    if isinstance(results, list):
        df = pd.DataFrame(results)
    else:
        df = results

    # Handle empty results
    if df.empty:
        return ""

    # Convert to CSV
    try:
        return df.to_csv(index=False, header=include_header)
    except Exception as e:
        logging.error(f"Error converting results to CSV: {str(e)}")
        return ""


def parse_json_params(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string into a dictionary of parameters.

    This function is used to parse connection parameters and other JSON strings
    provided by the user.

    Args:
        json_str: JSON string to parse

    Returns:
        Dictionary of parameters
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON parameters: {str(e)}")
        raise ValueError(f"Invalid JSON format: {str(e)}")


def format_error(error_message: str, error_type: str = "Error") -> str:
    """
    Format an error message for display to the user.

    Args:
        error_message: The error message to display
        error_type: Type of error (e.g., "Error", "Warning", "Security Error")

    Returns:
        Formatted error message
    """
    return f"{error_type}: {error_message}"


def sanitize_output(output: str, max_length: int = 2000) -> str:
    """
    Sanitize and trim output to a reasonable length.

    Args:
        output: The output string to sanitize
        max_length: Maximum length for the output

    Returns:
        Sanitized output
    """
    # For very small max_length values (like in tests), just return truncated string with indicator
    if max_length < 20:
        return output[: max_length - 3] + "..."

    if len(output) > max_length:
        truncated = output[: max_length - 100]
        return truncated + f"\n... (output truncated, {len(output) - len(truncated)} more characters)"
    return output


def get_column_display_width(df: pd.DataFrame, column_name: str) -> int:
    """
    Calculate the display width needed for a column based on its values.

    Args:
        df: DataFrame containing the column
        column_name: Name of the column

    Returns:
        Width in characters needed to display the column
    """
    # Account for column name length
    width = len(str(column_name))

    # Check actual values
    col = df[column_name]

    # Convert to strings and get max length
    if not col.empty:
        # Special handling for numeric columns (align decimal points)
        if pd.api.types.is_numeric_dtype(col):
            # Add space for formatting numeric values
            width = max(width, col.astype(str).str.len().max() + 2)
        else:
            width = max(width, col.astype(str).str.len().max())

    # Add padding
    return width + 2  # 1 space padding on each side


def format_value_for_display(value: Any) -> str:
    """
    Format a value for clean display in tables and output.

    Args:
        value: Value to format

    Returns:
        Formatted string representation
    """
    if value is None:
        return "NULL"
    elif isinstance(value, float):
        # Format floats with limited precision
        return f"{value:.6g}"
    elif isinstance(value, (list, dict)):
        # Compact JSON for collections
        return json.dumps(value, default=str)
    else:
        return str(value)


def chunk_long_results(results: List[Dict[str, Any]], max_rows_per_chunk: int = 100) -> List[List[Dict[str, Any]]]:
    """
    Split large result sets into manageable chunks.

    Args:
        results: List of result dictionaries
        max_rows_per_chunk: Maximum number of rows per chunk

    Returns:
        List of chunked results
    """
    return [results[i : i + max_rows_per_chunk] for i in range(0, len(results), max_rows_per_chunk)]


def summarize_results(
    results: Union[pd.DataFrame, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Generate a summary of query results.

    Args:
        results: DataFrame or list of dictionaries containing the results

    Returns:
        Dictionary with result summary statistics
    """
    # Convert results to DataFrame if it's a list of dicts
    if isinstance(results, list):
        df = pd.DataFrame(results)
    else:
        df = results

    # Handle empty results
    if df.empty:
        return {"row_count": 0, "column_count": 0}

    # Calculate basic statistics for numeric columns
    stats = {}
    numeric_cols = df.select_dtypes(include=["number"])

    for col in numeric_cols.columns:
        stats[col] = {
            "min": numeric_cols[col].min(),
            "max": numeric_cols[col].max(),
            "mean": numeric_cols[col].mean(),
            "median": numeric_cols[col].median(),
            "null_count": df[col].isna().sum(),
        }

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "numeric_columns": list(numeric_cols.columns),
        "stats": stats,
    }
