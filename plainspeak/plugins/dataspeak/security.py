"""
DataSpeak Security Module

This module provides security checks for SQL queries to prevent unsafe operations
and protect user data. It implements multiple layers of defense:

1. SQL syntax validation
2. Command whitelisting
3. Query analysis for potentially dangerous operations
4. Parameter sanitization
"""

import logging
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Try to import SQLGlot for SQL parsing and validation
try:
    import sqlglot
    from sqlglot.errors import ParseError

    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False
    logging.warning("sqlglot not found, falling back to regex-based SQL validation")


class SecurityLevel(Enum):
    """Security levels for DataSpeak operations."""

    LOW = 0  # Allow most operations, minimal checking
    MEDIUM = 1  # Block unsafe operations, allow modifications within constraints
    HIGH = 2  # Read-only mode, no modifications allowed
    PARANOID = 3  # Strict whitelist, parameter binding, full validation


class SecurityViolation(Exception):
    """Exception raised when a security violation is detected in a query."""


# SQL command whitelist by security level
ALLOWED_COMMANDS = {
    SecurityLevel.LOW: [
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "ALTER",
        "DROP",
        "EXPLAIN",
        "ANALYZE",
        "WITH",
        "PRAGMA",
        "SHOW",
    ],
    SecurityLevel.MEDIUM: [
        "SELECT",
        "INSERT",
        "UPDATE",
        "CREATE TABLE",
        "CREATE VIEW",
        "ALTER TABLE",
        "WITH",
        "EXPLAIN",
        "ANALYZE",
        "PRAGMA",
        "SHOW",
    ],
    SecurityLevel.HIGH: ["SELECT", "EXPLAIN", "ANALYZE", "PRAGMA", "SHOW"],
    SecurityLevel.PARANOID: ["SELECT"],
}

# Dangerous patterns to check for
DANGEROUS_PATTERNS = [
    (
        r";\s*[^\s]",
        "Multiple statements detected",
    ),  # SQL injection via multiple statements
    (r"--", "SQL comment detected"),  # Comments might hide malicious code
    (
        r"/\*.*?\*/",
        "SQL comment block detected",
    ),  # Block comments might hide malicious code
    (r"EXECUTE\s+", "Dynamic SQL execution detected"),  # Dynamic SQL execution
    (r"INTO\s+OUTFILE", "File write operation detected"),  # File operations
    (r"LOAD\s+DATA", "File read operation detected"),  # File operations
    (r"\bEXEC\b", "Potential command execution"),  # Exec commands
    (r"xp_cmdshell", "System command execution"),  # MS SQL specific
    (r"sp_execute", "Dynamic SQL execution"),  # Stored procedure execution
    (r"GRANT\s+", "Permission modification"),  # Permissions
    (r"REVOKE\s+", "Permission modification"),  # Permissions
    (r"UNION\s+(?:ALL\s+)?SELECT", "UNION injection attempt"),  # UNION-based SQLi
]


class SQLSecurityChecker:
    """
    Security checker for SQL queries.

    This class provides methods to validate and sanitize SQL queries
    to prevent unsafe operations.
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.HIGH):
        """
        Initialize the SQL security checker.

        Args:
            security_level: The security level to enforce.
        """
        self.security_level = security_level
        self.logger = logging.getLogger("plainspeak.dataspeak.security")

    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a SQL query for security violations.

        Args:
            query: The SQL query to validate.

        Returns:
            A tuple of (is_valid, error_message).
        """
        # Check for empty query
        if not query or not query.strip():
            return False, "Empty query"

        # Check SQL syntax if SQLGlot is available
        if HAS_SQLGLOT:
            try:
                parsed = sqlglot.parse(query)
                if not parsed:
                    return False, "Failed to parse SQL syntax"
            except ParseError as e:
                return False, f"SQL syntax error: {str(e)}"
            except Exception as e:
                self.logger.warning(f"Unexpected error during SQL parsing: {e}")
                # Continue with other checks

        # Check for multiple statements
        if ";" in query and re.search(r";\s*[^\s]", query):
            return False, "Multiple SQL statements are not allowed"

        # Check for allowed commands
        command_match = re.match(r"^\s*([A-Za-z]+)", query)
        if not command_match:
            return False, "Could not identify SQL command"

        command = command_match.group(1).upper()
        allowed = ALLOWED_COMMANDS[self.security_level]

        if command not in allowed:
            return (
                False,
                f"Command '{command}' not allowed at security level {self.security_level.name}",
            )

        # Check for dangerous patterns
        for pattern, message in DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False, message

        # Additional security checks based on level
        if self.security_level in [SecurityLevel.HIGH, SecurityLevel.PARANOID]:
            # For HIGH and PARANOID levels, ensure no data modification
            if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER)\b", query, re.IGNORECASE):
                return False, "Data modification not allowed at this security level"

        if self.security_level == SecurityLevel.PARANOID:
            # For PARANOID level, perform additional checks
            if not re.match(r"^\s*SELECT\b", query, re.IGNORECASE):
                return False, "Only simple SELECT queries allowed in paranoid mode"
            if re.search(r"\bINTO\b", query, re.IGNORECASE):
                return False, "INTO clause not allowed in paranoid mode"

        return True, None

    def sanitize_query(self, query: str) -> str:
        """
        Sanitize a SQL query by removing potentially dangerous elements.

        This is a basic sanitization and should not be relied upon as the only
        security measure. Always use validate_query first.

        Args:
            query: The SQL query to sanitize.

        Returns:
            A sanitized version of the query.
        """
        # Remove comments
        sanitized = re.sub(r"--.*?(\n|$)", " ", query)  # Line comments
        sanitized = re.sub(r"/\*.*?\*/", " ", sanitized, flags=re.DOTALL)  # Block comments

        # Remove multiple statements
        if ";" in sanitized:
            sanitized = sanitized.split(";")[0] + ";"

        return sanitized

    def bind_parameters(self, query: str, params: Dict[str, Any]) -> str:
        """
        Safely bind parameters to a query string.

        Args:
            query: The SQL query with parameter placeholders.
            params: Dictionary of parameter values.

        Returns:
            A query with parameters safely inserted.
        """
        if not HAS_SQLGLOT:
            self.logger.warning("sqlglot not available, parameter binding may be less secure")
            # Basic parameter binding - should only be used when sqlglot is unavailable
            result = query
            for key, value in params.items():
                placeholder = f":{key}"
                if isinstance(value, str):
                    # Escape single quotes in strings
                    escaped_value = value.replace("'", "''")
                    result = result.replace(placeholder, f"'{escaped_value}'")
                elif value is None:
                    result = result.replace(placeholder, "NULL")
                else:
                    result = result.replace(placeholder, str(value))
            return result
        else:
            # Use sqlglot for proper parameter binding when available
            try:
                # Parse the query to ensure it's valid SQL before binding
                sqlglot.parse_one(query)

                # Convert parameters to the correct format
                # This uses sqlglot's internal logic to properly escape and format values
                bound_query = sqlglot.transpile(
                    query,
                    read="duckdb",  # Assuming DuckDB dialect
                    write="duckdb",
                    params=params,
                )[0]

                return bound_query
            except Exception as e:
                raise SecurityViolation(f"Parameter binding failed: {str(e)}")

    def analyze_query_risk(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query for potential risks.

        Args:
            query: The SQL query to analyze.

        Returns:
            A dictionary containing risk assessment.
        """
        risk_level = "low"
        risk_factors = []

        # Check for modification operations
        if re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER)\b", query, re.IGNORECASE):
            risk_level = "high"
            risk_factors.append("Data modification")

        # Check for large result potential
        if not re.search(r"\bLIMIT\b\s+\d+", query, re.IGNORECASE) and "SELECT" in query.upper():
            risk_level = max(risk_level, "medium")
            risk_factors.append("Unlimited result size")

        # Check for complex joins
        join_count = len(re.findall(r"\bJOIN\b", query, re.IGNORECASE))
        if join_count > 2:
            risk_level = max(risk_level, "medium")
            risk_factors.append(f"Complex query with {join_count} joins")

        # Check for full table scans
        if "WHERE" not in query.upper() and "SELECT" in query.upper():
            risk_level = max(risk_level, "medium")
            risk_factors.append("Full table scan")

        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": self._get_recommendation(risk_level, risk_factors),
        }

    def _get_recommendation(self, risk_level: str, risk_factors: List[str]) -> str:
        """Generate a recommendation based on risk assessment."""
        if risk_level == "low":
            return "Query appears safe to execute"

        recommendations = []
        if "Data modification" in risk_factors:
            recommendations.append("Review data modification carefully before execution")

        if "Unlimited result size" in risk_factors:
            recommendations.append("Consider adding a LIMIT clause")

        if "Complex query" in risk_factors:
            recommendations.append("Verify query efficiency and consider optimization")

        if "Full table scan" in risk_factors:
            recommendations.append("Consider adding a WHERE clause for better performance")

        return "; ".join(recommendations)


def is_safe_query(query: str, security_level: SecurityLevel = SecurityLevel.HIGH) -> Tuple[bool, Optional[str]]:
    """
    Check if a SQL query is safe to execute.

    This is a convenience function that creates a SQLSecurityChecker and validates the query.

    Args:
        query: The SQL query to check.
        security_level: The security level to enforce.

    Returns:
        A tuple of (is_safe, error_message).
    """
    checker = SQLSecurityChecker(security_level)
    return checker.validate_query(query)


def sanitize_and_check_query(
    query: str,
    params: Optional[Dict[str, Any]] = None,
    security_level: SecurityLevel = SecurityLevel.HIGH,
) -> Tuple[str, Dict[str, Any]]:
    """
    Sanitize and check a SQL query for safety.

    Args:
        query: The SQL query to check and sanitize.
        params: Optional parameters to bind to the query.
        security_level: The security level to enforce.

    Returns:
        A tuple of (sanitized_query, risk_assessment).

    Raises:
        SecurityViolation: If the query fails security checks.
    """
    checker = SQLSecurityChecker(security_level)

    # First, validate the query
    is_valid, error = checker.validate_query(query)
    if not is_valid:
        raise SecurityViolation(f"SQL security violation: {error}")

    # Then sanitize the query
    sanitized = checker.sanitize_query(query)

    # Bind parameters if provided
    if params:
        sanitized = checker.bind_parameters(sanitized, params)

    # Analyze risks
    risk_assessment = checker.analyze_query_risk(sanitized)

    return sanitized, risk_assessment
