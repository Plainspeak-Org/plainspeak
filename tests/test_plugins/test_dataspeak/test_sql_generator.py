"""
Tests for the SQL Generator module of the DataSpeak plugin.
"""

from unittest.mock import MagicMock, patch

from plainspeak.plugins.dataspeak.security import SecurityLevel
from plainspeak.plugins.dataspeak.sql_generator import (
    QueryTemplate,
    SQLGenerator,
    generate_sql_from_text,
    get_sql_generator,
)


class TestQueryTemplate:
    """Tests for the QueryTemplate class."""

    def test_init(self):
        """Test initialization with various parameters."""
        # Test with minimal parameters
        template = QueryTemplate("SELECT * FROM table")
        assert template.template == "SELECT * FROM table"
        assert template.params == {}
        assert template.requires_columns == []
        assert template.requires_tables == []
        assert template.description == ""

        # Test with all parameters
        template = QueryTemplate(
            "SELECT :column FROM :table WHERE :condition",
            params={"condition": "1=1"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Test template",
        )
        assert template.template == "SELECT :column FROM :table WHERE :condition"
        assert template.params == {"condition": "1=1"}
        assert template.requires_columns == ["column"]
        assert template.requires_tables == ["table"]
        assert template.description == "Test template"

    def test_fill(self):
        """Test template filling with parameters."""
        # Simple template
        template = QueryTemplate("SELECT * FROM :table")
        sql = template.fill({"table": "users"})
        assert sql == "SELECT * FROM 'users'"

        # Template with default params
        template = QueryTemplate("SELECT * FROM :table LIMIT :limit", params={"limit": 100})
        # Override default param
        sql = template.fill({"table": "users", "limit": 10})
        assert sql == "SELECT * FROM 'users' LIMIT 10"
        # Use default param
        sql = template.fill({"table": "users"})
        assert sql == "SELECT * FROM 'users' LIMIT 100"

        # Test with string values that need escaping
        template = QueryTemplate("SELECT * FROM :table WHERE name = :name")
        sql = template.fill({"table": "users", "name": "O'Connor"})
        assert sql == "SELECT * FROM 'users' WHERE name = 'O''Connor'"

        # Test with NULL value
        template = QueryTemplate("SELECT * FROM :table WHERE column IS :value")
        sql = template.fill({"table": "users", "value": None})
        assert sql == "SELECT * FROM 'users' WHERE column IS NULL"

        # Test with list value
        template = QueryTemplate("SELECT * FROM :table WHERE id IN (:ids)")
        sql = template.fill({"table": "users", "ids": [1, 2, 3]})
        assert sql == "SELECT * FROM 'users' WHERE id IN (1, 2, 3)"

        # Test with list of strings
        template = QueryTemplate("SELECT * FROM :table WHERE name IN (:names)")
        sql = template.fill({"table": "users", "names": ["Alice", "Bob", "Charlie"]})
        assert sql == "SELECT * FROM 'users' WHERE name IN ('Alice', 'Bob', 'Charlie')"

    def test_is_compatible(self):
        """Test compatibility check with available columns and tables."""
        # Template with no requirements
        template = QueryTemplate("SELECT 1")
        assert template.is_compatible([], [])
        assert template.is_compatible(["col1"], ["table1"])

        # Template requiring specific tables
        template = QueryTemplate("SELECT * FROM :table", requires_tables=["users"])
        assert template.is_compatible([], ["users"])
        assert template.is_compatible([], ["users", "products"])
        assert not template.is_compatible([], ["products"])

        # Template requiring specific columns
        template = QueryTemplate("SELECT :column FROM :table", requires_columns=["name"], requires_tables=["users"])
        assert template.is_compatible(["name"], ["users"])
        assert template.is_compatible(["name", "email"], ["users"])
        assert not template.is_compatible(["email"], ["users"])
        assert not template.is_compatible(["name"], ["products"])


class TestSQLGenerator:
    """Tests for the SQLGenerator class."""

    def test_init(self):
        """Test initialization with various parameters."""
        # Test with default parameters
        generator = SQLGenerator()
        assert generator.security_level == SecurityLevel.HIGH
        assert generator.enable_llm is False
        assert len(generator.templates) > 0
        assert "select_all" in generator.templates

        # Test with custom security level
        generator = SQLGenerator(security_level=SecurityLevel.LOW)
        assert generator.security_level == SecurityLevel.LOW

        # Test with LLM enabled
        generator = SQLGenerator(enable_llm=True)
        assert generator.enable_llm is True

    @patch("plainspeak.plugins.dataspeak.sql_generator.SQLSecurityChecker")
    def test_generate_sql_pattern_matching(self, mock_security_checker):
        """Test SQL generation using pattern matching."""
        # Setup mock security checker
        mock_checker = MagicMock()
        mock_checker.validate_query.return_value = (True, None)
        mock_security_checker.return_value = mock_checker

        # Create generator
        generator = SQLGenerator()

        # Test with pattern for selecting all records
        sql, params = generator.generate_sql("show all records from users", available_tables=["users", "products"])
        assert "SELECT * FROM" in sql
        assert "users" in sql
        assert "LIMIT" in sql

        # Test with pattern for counting records
        sql, params = generator.generate_sql(
            "how many records are there in users", available_tables=["users", "products"]
        )
        assert "SELECT COUNT(*) FROM" in sql
        assert "users" in sql

        # Test with pattern for filtering by equality
        sql, params = generator.generate_sql(
            "show all records from users where name equals John", available_tables=["users", "products"]
        )
        assert "SELECT * FROM" in sql
        assert "users" in sql
        assert "WHERE" in sql
        assert "name" in sql
        assert "John" in sql or params.get("value") == "John"

    @patch("plainspeak.plugins.dataspeak.sql_generator.SQLSecurityChecker")
    def test_generate_sql_template_matching(self, mock_security_checker):
        """Test SQL generation using template matching."""
        # Setup mock security checker
        mock_checker = MagicMock()
        mock_checker.validate_query.return_value = (True, None)
        mock_security_checker.return_value = mock_checker

        # Create generator
        generator = SQLGenerator()

        # Test with keyword-based template matching
        sql, params = generator.generate_sql(
            "find the total sales from invoices",
            available_tables=["invoices"],
            available_columns={"invoices": ["id", "customer_id", "amount", "date"]},
        )
        assert "SELECT" in sql
        assert "invoices" in sql
        assert "amount" in sql or "SUM" in sql

        # Test with count and group by
        sql, params = generator.generate_sql(
            "count orders group by customer_id",
            available_tables=["orders"],
            available_columns={"orders": ["id", "customer_id", "amount", "date"]},
        )
        assert "SELECT" in sql
        assert "orders" in sql
        assert "GROUP BY" in sql
        assert "customer_id" in sql
        assert "COUNT" in sql

    @patch("plainspeak.plugins.dataspeak.sql_generator.SQLSecurityChecker")
    def test_explain_query(self, mock_security_checker):
        """Test query explanation generation."""
        # Setup mock security checker
        mock_checker = MagicMock()
        mock_checker.validate_query.return_value = (True, None)
        mock_security_checker.return_value = mock_checker

        # Create generator
        generator = SQLGenerator()

        # Test explaining a SELECT query
        explanation = generator.explain_query("SELECT * FROM users WHERE age > 18 ORDER BY name LIMIT 10")
        assert "retrieves" in explanation.lower()
        assert "users" in explanation
        assert "age > 18" in explanation
        assert "sorted by name" in explanation
        assert "limited to 10" in explanation

        # Test explaining a COUNT query
        explanation = generator.explain_query("SELECT COUNT(*) FROM products")
        assert "counts" in explanation.lower()
        assert "products" in explanation

        # Test explaining an aggregate query
        explanation = generator.explain_query("SELECT AVG(price) FROM products WHERE category = 'Electronics'")
        assert "average" in explanation.lower()
        assert "products" in explanation


class TestHelperFunctions:
    """Tests for the helper functions in sql_generator.py."""

    def test_get_sql_generator(self):
        """Test get_sql_generator function."""
        # Test with default parameters
        generator = get_sql_generator()
        assert isinstance(generator, SQLGenerator)
        assert generator.security_level == SecurityLevel.HIGH

        # Test with custom security level
        generator = get_sql_generator(SecurityLevel.LOW)
        assert generator.security_level == SecurityLevel.LOW

    @patch("plainspeak.plugins.dataspeak.sql_generator.get_sql_generator")
    def test_generate_sql_from_text(self, mock_get_generator):
        """Test generate_sql_from_text function."""
        # Setup mock generator
        mock_generator = MagicMock()
        mock_generator.generate_sql.return_value = ("SELECT * FROM users", {"table": "users"})
        mock_get_generator.return_value = mock_generator

        # Test function
        sql, params = generate_sql_from_text("show me all users", available_tables=["users", "products"])

        # Verify results
        assert sql == "SELECT * FROM users"
        assert params == {"table": "users"}

        # Verify correct security level was used
        mock_get_generator.assert_called_once_with(SecurityLevel.HIGH)

        # Test with custom security level
        sql, params = generate_sql_from_text(
            "show me all users", available_tables=["users", "products"], security_level=SecurityLevel.LOW
        )

        # Verify correct security level was used
        mock_get_generator.assert_called_with(SecurityLevel.LOW)
