"""
Tests for the Security module of the DataSpeak plugin.
"""

from unittest.mock import MagicMock, patch

import pytest

from plainspeak.plugins.dataspeak.security import (
    SecurityLevel,
    SQLSecurityChecker,
    is_safe_query,
    sanitize_and_check_query,
)


class TestSecurityLevel:
    """Tests for the SecurityLevel enum."""

    def test_enum_values(self):
        """Test enum values."""
        assert SecurityLevel.LOW.value < SecurityLevel.MEDIUM.value
        assert SecurityLevel.MEDIUM.value < SecurityLevel.HIGH.value
        assert SecurityLevel.HIGH.value < SecurityLevel.PARANOID.value

    def test_comparisons(self):
        """Test enum comparisons."""
        assert SecurityLevel.LOW < SecurityLevel.MEDIUM
        assert SecurityLevel.MEDIUM < SecurityLevel.HIGH
        assert SecurityLevel.HIGH < SecurityLevel.PARANOID
        assert SecurityLevel.PARANOID > SecurityLevel.HIGH
        assert SecurityLevel.HIGH >= SecurityLevel.HIGH


class TestSQLSecurityChecker:
    """Tests for the SQLSecurityChecker class."""

    def test_init(self):
        """Test initialization with various security levels."""
        # Test with default level
        checker = SQLSecurityChecker()
        assert checker.security_level == SecurityLevel.HIGH

        # Test with custom level
        checker = SQLSecurityChecker(SecurityLevel.LOW)
        assert checker.security_level == SecurityLevel.LOW

    def test_validate_query_syntax(self):
        """Test query syntax validation."""
        checker = SQLSecurityChecker()

        # Valid query
        is_valid, error = checker.validate_query_syntax("SELECT * FROM users")
        assert is_valid is True
        assert error is None

        # Invalid query
        is_valid, error = checker.validate_query_syntax("SELEC * FROMM users")
        assert is_valid is False
        assert error is not None
        assert "syntax" in error.lower()

    def test_is_safe_operation(self):
        """Test operation safety checks."""
        checker = SQLSecurityChecker()

        # Test SELECT (always safe)
        assert checker.is_safe_operation("SELECT * FROM users") is True

        # Test with HIGH security level (read-only)
        checker = SQLSecurityChecker(SecurityLevel.HIGH)
        assert checker.is_safe_operation("SELECT * FROM users") is True
        assert checker.is_safe_operation("INSERT INTO users VALUES (1, 'test')") is False
        assert checker.is_safe_operation("UPDATE users SET name = 'test'") is False
        assert checker.is_safe_operation("DELETE FROM users") is False
        assert checker.is_safe_operation("DROP TABLE users") is False

        # Test with LOW security level (more permissive)
        checker = SQLSecurityChecker(SecurityLevel.LOW)
        assert checker.is_safe_operation("SELECT * FROM users") is True
        assert checker.is_safe_operation("INSERT INTO users VALUES (1, 'test')") is True
        assert checker.is_safe_operation("UPDATE users SET name = 'test'") is True
        assert checker.is_safe_operation("DELETE FROM users") is True
        # DROP should still be blocked even at LOW level
        assert checker.is_safe_operation("DROP TABLE users") is False

    def test_check_for_dangerous_patterns(self):
        """Test detection of dangerous patterns."""
        checker = SQLSecurityChecker()

        # Safe query
        dangerous, reason = checker.check_for_dangerous_patterns("SELECT * FROM users WHERE id = 1")
        assert dangerous is False
        assert reason is None

        # Query with SQL injection attempt
        dangerous, reason = checker.check_for_dangerous_patterns("SELECT * FROM users WHERE name = 'test' OR 1=1--'")
        assert dangerous is True
        assert reason is not None
        assert "injection" in reason.lower()

        # Query with multiple statements
        dangerous, reason = checker.check_for_dangerous_patterns("SELECT * FROM users; DROP TABLE users;")
        assert dangerous is True
        assert reason is not None
        assert "multiple" in reason.lower() or "statement" in reason.lower()

    def test_validate_query(self):
        """Test the complete query validation process."""
        checker = SQLSecurityChecker()

        # Safe query at HIGH level
        is_valid, error = checker.validate_query("SELECT * FROM users WHERE id = 1")
        assert is_valid is True
        assert error is None

        # Data modification at HIGH level (should fail)
        is_valid, error = checker.validate_query("INSERT INTO users VALUES (1, 'test')")
        assert is_valid is False
        assert error is not None

        # Data modification at LOW level (should pass)
        checker = SQLSecurityChecker(SecurityLevel.LOW)
        is_valid, error = checker.validate_query("INSERT INTO users VALUES (1, 'test')")
        assert is_valid is True
        assert error is None

        # Dangerous query at any level (should fail)
        is_valid, error = checker.validate_query("SELECT * FROM users WHERE name = 'test' OR 1=1--'")
        assert is_valid is False
        assert error is not None

        # Query with syntax error at any level (should fail)
        is_valid, error = checker.validate_query("SELEC * FROMM users")
        assert is_valid is False
        assert error is not None


class TestHelperFunctions:
    """Tests for the helper functions in security.py."""

    @patch("plainspeak.plugins.dataspeak.security.SQLSecurityChecker")
    def test_is_safe_query(self, mock_checker_class):
        """Test is_safe_query helper function."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker.validate_query.return_value = (True, None)
        mock_checker_class.return_value = mock_checker

        # Test function
        result = is_safe_query("SELECT * FROM users", security_level=SecurityLevel.HIGH)

        # Verify result
        assert result is True

        # Verify correct security level was used
        mock_checker_class.assert_called_once_with(SecurityLevel.HIGH)
        mock_checker.validate_query.assert_called_once_with("SELECT * FROM users")

        # Test with unsafe query
        mock_checker.validate_query.return_value = (False, "Error message")
        result = is_safe_query("DROP TABLE users")
        assert result is False

    @patch("plainspeak.plugins.dataspeak.security.SQLSecurityChecker")
    def test_sanitize_and_check_query(self, mock_checker_class):
        """Test sanitize_and_check_query helper function."""
        # Setup mock
        mock_checker = MagicMock()
        mock_checker.validate_query.return_value = (True, None)
        mock_checker_class.return_value = mock_checker

        # Test with parameters
        query = "SELECT * FROM users WHERE id = :id"
        params = {"id": 1}

        safe_query, is_safe = sanitize_and_check_query(query, params, security_level=SecurityLevel.HIGH)

        assert is_safe is True
        assert "SELECT * FROM users WHERE id = 1" in safe_query

        # Test with unsafe query
        mock_checker.validate_query.return_value = (False, "Error message")

        with pytest.raises(ValueError):
            sanitize_and_check_query("DROP TABLE users", None, security_level=SecurityLevel.HIGH)
