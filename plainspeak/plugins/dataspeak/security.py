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

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


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
    (r"--", "SQL comment detected - possible SQL injection"),  # Comments might hide malicious code
    (
        r"/\*.*?\*/",
        "SQL comment block detected - possible SQL injection",
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
        syntax_valid, syntax_error = self.validate_query_syntax(query)
        if not syntax_valid:
            return False, syntax_error

        # Check for multiple statements
        if ";" in query and re.search(r";\s*[^\s]", query):
            return False, "Multiple SQL statements are not allowed"

        # Check for allowed commands
        command_match = re.match(r"^\s*([A-Za-z]+)", query)
        if not command_match:
            return False, "Could not identify SQL command"

        command_match.group(1).upper()

        # Check if the operation is safe for the current security level
        operation_safe = self.is_safe_operation(query)
        if not operation_safe:
            return False, "Operation not allowed at this security level"

        # Check for dangerous patterns
        has_dangerous_pattern, pattern_error = self.check_for_dangerous_patterns(query)
        if has_dangerous_pattern:
            return False, pattern_error

        return True, None

    def validate_query_syntax(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the syntax of a SQL query.

        Args:
            query: The SQL query to validate.

        Returns:
            A tuple of (is_valid, error_message).
        """
        if not HAS_SQLGLOT:
            self.logger.warning("sqlglot not available, parameter binding may be less secure")
            # Simple regex-based validation as fallback
            try:
                # Simple check for basic SQL syntax
                if not re.match(
                    r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|SHOW|EXPLAIN|WITH|ANALYZE)\s+",
                    query,
                    re.IGNORECASE,
                ):
                    return False, "Syntax error: Query doesn't start with a valid SQL command"

                # Check for balanced parentheses
                if query.count("(") != query.count(")"):
                    return False, "Syntax error: Unbalanced parentheses"

                # Check for FROM clause in SELECT
                if re.match(r"^\s*SELECT\s+", query, re.IGNORECASE) and not re.search(
                    r"\sFROM\s+", query, re.IGNORECASE
                ):
                    return False, "Syntax error: SELECT missing FROM clause"

                # Basic validation passed
                return True, None
            except Exception as e:
                return False, f"Syntax error: {str(e)}"

        try:
            parsed = sqlglot.parse(query)
            if not parsed:
                return False, "Failed to parse SQL syntax"
            return True, None
        except ParseError as e:
            return False, f"SQL syntax error: {str(e)}"
        except Exception as e:
            self.logger.warning(f"Unexpected error during SQL parsing: {e}")
            # Continue with other checks
            return True, None

    def is_safe_operation(self, query: str) -> bool:
        """
        Check if the SQL operation is safe for the current security level.

        Args:
            query: The SQL query to check.

        Returns:
            True if the operation is safe, False otherwise.
        """
        # Extract command
        command_match = re.match(r"^\s*([A-Za-z]+)", query)
        if not command_match:
            return False

        command = command_match.group(1).upper()
        allowed = ALLOWED_COMMANDS[self.security_level]

        if command not in allowed:
            return False

        # Block DROP operations at all security levels
        if re.search(r"\bDROP\b", query, re.IGNORECASE):
            return False

        # Additional security checks based on level
        if self.security_level in [SecurityLevel.HIGH, SecurityLevel.PARANOID]:
            # For HIGH and PARANOID levels, ensure no data modification
            if re.search(r"\b(INSERT|UPDATE|DELETE|ALTER)\b", query, re.IGNORECASE):
                return False

        if self.security_level == SecurityLevel.PARANOID:
            # For PARANOID level, perform additional checks
            if not re.match(r"^\s*SELECT\b", query, re.IGNORECASE):
                return False
            if re.search(r"\bINTO\b", query, re.IGNORECASE):
                return False

        return True

    def check_for_dangerous_patterns(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check a SQL query for dangerous patterns.

        Args:
            query: The SQL query to check.

        Returns:
            A tuple of (has_dangerous_pattern, error_message).
        """
        for pattern, message in DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return True, message

        return False, None

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
            Query with parameters bound.
        """
        if not params:
            return query

        # Use simple string replacement for parameter binding
        bound_query = query
        for key, value in params.items():
            placeholder = f":{key}"

            # Format the value based on its type
            if isinstance(value, str):
                # Escape single quotes in strings
                escaped_value = value.replace("'", "''")
                formatted_value = f"'{escaped_value}'"
            elif value is None:
                formatted_value = "NULL"
            else:
                formatted_value = str(value)

            # Replace the placeholder
            bound_query = bound_query.replace(placeholder, formatted_value)

        return bound_query

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


def is_safe_query(query: str, security_level: SecurityLevel = SecurityLevel.HIGH) -> bool:
    """
    Check if a query is safe at the given security level.

    Args:
        query: The SQL query to check.
        security_level: The security level to enforce.

    Returns:
        True if the query is safe, False otherwise.
    """
    checker = SQLSecurityChecker(security_level)
    is_valid, _ = checker.validate_query(query)
    return is_valid


def sanitize_and_check_query(
    query: str,
    params: Optional[Dict[str, Any]] = None,
    security_level: SecurityLevel = SecurityLevel.HIGH,
) -> Tuple[str, bool]:
    """
    Sanitize a query and check if it's safe.

    Args:
        query: The SQL query to check.
        params: Optional parameters to bind.
        security_level: The security level to enforce.

    Returns:
        A tuple of (sanitized_query, is_safe).

    Raises:
        ValueError: If the query fails security checks.
    """
    checker = SQLSecurityChecker(security_level)

    # First, validate the query
    is_valid, error = checker.validate_query(query)
    if not is_valid:
        raise ValueError(f"SQL security violation: {error}")

    # Sanitize the query
    sanitized = checker.sanitize_query(query)

    # Bind parameters if provided
    if params:
        sanitized = checker.bind_parameters(sanitized, params)

    # Check if the query is safe
    is_safe = True

    return sanitized, is_safe
