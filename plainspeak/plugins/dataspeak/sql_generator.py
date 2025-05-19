"""
DataSpeak SQL Generator Module

This module transforms natural language queries into SQL statements using
a combination of pattern matching, templates, and optional LLM assistance.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

# Try to import optional NLP dependencies
try:
    pass

    HAS_SQLITE = True
except ImportError:
    HAS_SQLITE = False
    logging.warning("sqlite3 not found, database operations will be limited")

# Import local modules
from plainspeak.plugins.dataspeak.security import SecurityLevel, SQLSecurityChecker


class QueryTemplate:
    """
    Template for SQL query generation with placeholders for values.

    This class represents a parametrized SQL query template that can be
    filled with specific values.
    """

    def __init__(
        self,
        template: str,
        params: Optional[Dict[str, Any]] = None,
        requires_columns: Optional[List[str]] = None,
        requires_tables: Optional[List[str]] = None,
        description: str = "",
    ):
        """
        Initialize a query template.

        Args:
            template: The SQL query template with placeholders
            params: Default parameter values
            requires_columns: Required column names in the data
            requires_tables: Required table names in the database
            description: Human-readable description of the template
        """
        self.template = template
        self.params = params or {}
        self.requires_columns = requires_columns or []
        self.requires_tables = requires_tables or []
        self.description = description

    def fill(self, params: Dict[str, Any]) -> str:
        """
        Fill the template with parameter values.

        Args:
            params: Parameter values to use

        Returns:
            The completed SQL query
        """
        # Combine default params with provided params
        all_params = {**self.params, **params}

        # Simple template replacement
        query = self.template
        for key, value in all_params.items():
            placeholder = f":{key}"

            # Handle different types of values
            if isinstance(value, str):
                # Escape string values
                safe_value = value.replace("'", "''")
                replacement = f"'{safe_value}'"
            elif value is None:
                replacement = "NULL"
            elif isinstance(value, (list, tuple)):
                # Format lists as comma-separated values
                formatted_values = []
                for item in value:
                    if isinstance(item, str):
                        safe_value = item.replace("'", "''")
                        formatted_values.append(f"'{safe_value}'")
                    else:
                        formatted_values.append(str(item))
                replacement = ", ".join(formatted_values)
            else:
                replacement = str(value)

            query = query.replace(placeholder, replacement)

        return query

    def is_compatible(self, available_columns: List[str], available_tables: List[str]) -> bool:
        """
        Check if this template is compatible with the available data schema.

        Args:
            available_columns: Available column names
            available_tables: Available table names

        Returns:
            True if compatible, False otherwise
        """
        # Check required columns
        for column in self.requires_columns:
            if column not in available_columns:
                return False

        # Check required tables
        for table in self.requires_tables:
            if table not in available_tables:
                return False

        return True


class SQLGenerator:
    """
    Transforms natural language queries into SQL statements.

    This class provides methods to generate SQL queries from natural
    language input using a combination of pattern matching, templates,
    and (optionally) LLM assistance.
    """

    DEFAULT_TEMPLATES = {
        "select_all": QueryTemplate(
            "SELECT * FROM :table LIMIT :limit",
            {"limit": "100"},
            requires_tables=["table"],
            description="Retrieve all records from a table",
        ),
        "count_all": QueryTemplate(
            "SELECT COUNT(*) FROM :table",
            requires_tables=["table"],
            description="Count all records in a table",
        ),
        "filter_equals": QueryTemplate(
            "SELECT * FROM :table WHERE :column = :value LIMIT :limit",
            {"limit": "100"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Filter records where a column equals a specific value",
        ),
        "filter_contains": QueryTemplate(
            "SELECT * FROM :table WHERE :column LIKE '%' || :value || '%' LIMIT :limit",
            {"limit": "100"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Filter records where a column contains a specific value",
        ),
        "filter_greater_than": QueryTemplate(
            "SELECT * FROM :table WHERE :column > :value LIMIT :limit",
            {"limit": "100"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Filter records where a column is greater than a specific value",
        ),
        "filter_less_than": QueryTemplate(
            "SELECT * FROM :table WHERE :column < :value LIMIT :limit",
            {"limit": "100"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Filter records where a column is less than a specific value",
        ),
        "group_by_count": QueryTemplate(
            "SELECT :column, COUNT(*) as count FROM :table GROUP BY :column ORDER BY count DESC LIMIT :limit",
            {"limit": "100"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Group records by a column and count occurrences",
        ),
        "aggregate_sum": QueryTemplate(
            "SELECT SUM(:column) FROM :table",
            requires_columns=["column"],
            requires_tables=["table"],
            description="Calculate the sum of a column",
        ),
        "aggregate_avg": QueryTemplate(
            "SELECT AVG(:column) FROM :table",
            requires_columns=["column"],
            requires_tables=["table"],
            description="Calculate the average of a column",
        ),
        "aggregate_min": QueryTemplate(
            "SELECT MIN(:column) FROM :table",
            requires_columns=["column"],
            requires_tables=["table"],
            description="Find the minimum value of a column",
        ),
        "aggregate_max": QueryTemplate(
            "SELECT MAX(:column) FROM :table",
            requires_columns=["column"],
            requires_tables=["table"],
            description="Find the maximum value of a column",
        ),
        "top_n": QueryTemplate(
            "SELECT * FROM :table ORDER BY :column DESC LIMIT :limit",
            {"limit": "10"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Get the top N records by a column",
        ),
        "bottom_n": QueryTemplate(
            "SELECT * FROM :table ORDER BY :column ASC LIMIT :limit",
            {"limit": "10"},
            requires_columns=["column"],
            requires_tables=["table"],
            description="Get the bottom N records by a column",
        ),
    }

    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.HIGH,
        templates_path: Optional[str] = None,
        enable_llm: bool = False,
    ):
        """
        Initialize the SQL Generator.

        Args:
            security_level: Security level for generated queries
            templates_path: Path to custom templates file
            enable_llm: Whether to use LLM assistance for query generation
        """
        self.logger = logging.getLogger("plainspeak.dataspeak.sql_generator")
        self.security_level = security_level
        self.security_checker = SQLSecurityChecker(security_level)
        self.enable_llm = enable_llm

        # Load templates
        self.templates = self.DEFAULT_TEMPLATES.copy()
        if templates_path:
            self._load_custom_templates(templates_path)

        # Natural language patterns for matching
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for matching natural language queries."""
        show_records_base = (
            r"(?:show|list|display|get) (?:all|everything|the)? (?:records|rows|data) "
            r"(?:from|in) (?:the )?(?P<table>\w+)"
        )

        filter_base = show_records_base + r" where (?P<column>\w+) "

        self.patterns = [
            # Show all records
            (show_records_base, "select_all", {"table": "table"}),
            # Count records
            (
                r"(?:how many|count) (?:records|rows) (?:are there )?(?:in|from) (?:the )?(?P<table>\w+)",
                "count_all",
                {"table": "table"},
            ),
            # Filter equals
            (
                filter_base + r"(?:is|=|equals|equal to) (?P<value>[^.]+)",
                "filter_equals",
                {"table": "table", "column": "column", "value": "value"},
            ),
            # Filter contains
            (
                filter_base + r"contains (?P<value>[^.]+)",
                "filter_contains",
                {"table": "table", "column": "column", "value": "value"},
            ),
            # Group by and count
            (
                r"(?:group|count) (?:by|on|with) (?P<column>\w+) (?:from|in) (?:the )?(?P<table>\w+)",
                "group_by_count",
                {"table": "table", "column": "column"},
            ),
            # Sum, average, min, max
            (
                r"(?:calculate|find|what is) the (?P<aggregation>sum|average|avg|minimum|min|maximum|max) "
                r"of (?P<column>\w+) (?:from|in) (?:the )?(?P<table>\w+)",
                "aggregate_generic",
                {"table": "table", "column": "column", "aggregation": "aggregation"},
            ),
            # Top N
            (
                r"(?:show|list|display|get) (?:the )?(?:top|highest|largest|best|most) (?P<limit>\d+) "
                r"(?P<column>\w+) (?:from|in) (?:the )?(?P<table>\w+)",
                "top_n",
                {"table": "table", "column": "column", "limit": "limit"},
            ),
            # Bottom N
            (
                r"(?:show|list|display|get) (?:the )?(?:bottom|lowest|smallest|worst|least) (?P<limit>\d+) "
                r"(?P<column>\w+) (?:from|in) (?:the )?(?P<table>\w+)",
                "bottom_n",
                {"table": "table", "column": "column", "limit": "limit"},
            ),
        ]

    def _load_custom_templates(self, templates_path: str):
        """
        Load custom query templates from a JSON file.

        Args:
            templates_path: Path to the JSON templates file
        """
        try:
            with open(templates_path, "r") as f:
                custom_templates = json.load(f)

            for name, template_data in custom_templates.items():
                self.templates[name] = QueryTemplate(
                    template=template_data["template"],
                    params=template_data.get("params"),
                    requires_columns=template_data.get("requires_columns"),
                    requires_tables=template_data.get("requires_tables"),
                    description=template_data.get("description", ""),
                )

            self.logger.info(f"Loaded {len(custom_templates)} custom templates")
        except Exception as e:
            self.logger.error(f"Error loading custom templates: {str(e)}")

    def generate_sql(
        self,
        natural_query: str,
        available_tables: List[str],
        available_columns: Optional[Dict[str, List[str]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a SQL query from a natural language query.

        Args:
            natural_query: The natural language query
            available_tables: List of available table names
            available_columns: Dictionary mapping table names to column lists
            context: Additional context for query generation

        Returns:
            A tuple of (sql_query, parameters)
        """
        context = context or {}

        # Try pattern matching first
        sql, params = self._match_pattern(natural_query, available_tables, available_columns)
        if sql:
            return sql, params

        # Try template matching with fuzzy table/column detection
        sql, params = self._match_template(natural_query, available_tables, available_columns)
        if sql:
            return sql, params

        # As a fallback, use a simple SELECT * query for a recognized table
        for table in available_tables:
            if table.lower() in natural_query.lower():
                template = self.templates["select_all"]
                params = {"table": table, "limit": "100"}
                sql = template.fill(params)
                return sql, params

        # If all else fails, choose the first table
        if available_tables:
            template = self.templates["select_all"]
            params = {"table": available_tables[0], "limit": "100"}
            sql = template.fill(params)
            return sql, params

        raise ValueError("Could not generate SQL from natural language query")

    def _match_pattern(
        self,
        query: str,
        available_tables: List[str],
        available_columns: Optional[Dict[str, List[str]]] = None,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Match the query against defined patterns.

        Args:
            query: The natural language query
            available_tables: List of available table names
            available_columns: Dictionary mapping table names to column lists

        Returns:
            A tuple of (sql_query, parameters) or (None, {}) if no match found
        """
        for pattern, template_name, param_mapping in self.patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Extract parameters from the regex match
                params = {}
                for param_name, match_group in param_mapping.items():
                    params[param_name] = match.group(match_group)

                # Handle special cases
                if template_name == "aggregate_generic":
                    # Map the aggregation type to the appropriate template
                    agg_type = params.pop("aggregation").lower()
                    if agg_type in ("sum", "total"):
                        template_name = "aggregate_sum"
                    elif agg_type in ("average", "avg", "mean"):
                        template_name = "aggregate_avg"
                    elif agg_type in ("minimum", "min"):
                        template_name = "aggregate_min"
                    elif agg_type in ("maximum", "max"):
                        template_name = "aggregate_max"

                # Validate parameters
                if "table" in params and params["table"] not in available_tables:
                    # Try case-insensitive matching for table name
                    found = False
                    for table in available_tables:
                        if table.lower() == params["table"].lower():
                            params["table"] = table
                            found = True
                            break
                    if not found:
                        continue  # Skip this pattern if table not found

                # Validate and normalize limit to string
                if "limit" in params:
                    limit_value = params["limit"]
                    if isinstance(limit_value, (int, str)):
                        params["limit"] = str(limit_value)

                # Fill the template
                template = self.templates.get(template_name)
                if template:
                    try:
                        sql = template.fill(params)
                        # Validate the generated SQL
                        is_valid, error = self.security_checker.validate_query(sql)
                        if is_valid:
                            return sql, params
                        else:
                            self.logger.warning(f"Security check failed for generated SQL: {error}")
                    except Exception as e:
                        self.logger.warning(f"Error filling template {template_name}: {str(e)}")

        return None, {}

    def _match_template(
        self,
        query: str,
        available_tables: List[str],
        available_columns: Optional[Dict[str, List[str]]] = None,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Try to match query to a template based on keywords.

        This is a simpler backup matching strategy for when patterns fail.

        Args:
            query: The natural language query
            available_tables: List of available table names
            available_columns: Dictionary mapping table names to column lists

        Returns:
            A tuple of (sql_query, parameters) or (None, {}) if no match found
        """
        query_lower = query.lower()

        # Try to extract a table name from the query
        table_name = None
        for table in available_tables:
            if table.lower() in query_lower:
                table_name = table
                break

        if not table_name:
            return None, {}

        # Try to extract columns
        columns = []
        if available_columns and table_name in available_columns:
            for column in available_columns[table_name]:
                if column.lower() in query_lower:
                    columns.append(column)

        # Simple keyword matching for templates
        params = {"table": table_name}

        if "count" in query_lower and "group" in query_lower and columns:
            params["column"] = columns[0]
            template = self.templates["group_by_count"]
        elif "count" in query_lower:
            template = self.templates["count_all"]
        elif any(word in query_lower for word in ["sum", "total"]) and columns:
            params["column"] = columns[0]
            template = self.templates["aggregate_sum"]
        elif any(word in query_lower for word in ["average", "avg", "mean"]) and columns:
            params["column"] = columns[0]
            template = self.templates["aggregate_avg"]
        elif any(word in query_lower for word in ["minimum", "min", "lowest"]) and columns:
            params["column"] = columns[0]
            template = self.templates["aggregate_min"]
        elif any(word in query_lower for word in ["maximum", "max", "highest"]) and columns:
            params["column"] = columns[0]
            template = self.templates["aggregate_max"]
        elif any(word in query_lower for word in ["top", "best", "highest"]) and columns:
            params["column"] = columns[0]
            params["limit"] = "10"  # Default limit
            # Try to extract a number from the query
            number_match = re.search(r"\b(\d+)\b", query_lower)
            if number_match:
                params["limit"] = str(number_match.group(1))
            template = self.templates["top_n"]
        elif any(word in query_lower for word in ["bottom", "worst", "lowest"]) and columns:
            params["column"] = columns[0]
            params["limit"] = "10"  # Default limit
            # Try to extract a number from the query
            number_match = re.search(r"\b(\d+)\b", query_lower)
            if number_match:
                params["limit"] = str(number_match.group(1))
            template = self.templates["bottom_n"]
        elif any(word in query_lower for word in ["where", "equals", "contains", "greater", "less"]) and columns:
            params["column"] = columns[0]
            # Try to extract a value
            value_pattern = r"(?:equals|is|contains|=)\s+['\"]*([^'\"]+?)['\"]*(?:\s|$|\.)"
            value_match = re.search(value_pattern, query_lower)

            if value_match:
                params["value"] = value_match.group(1).strip()
                if "contains" in query_lower:
                    template = self.templates["filter_contains"]
                else:
                    template = self.templates["filter_equals"]
            else:
                # Default to select all
                template = self.templates["select_all"]
        else:
            # Default to select all
            template = self.templates["select_all"]

        # Fill the template and validate
        try:
            sql = template.fill(params)
            is_valid, error = self.security_checker.validate_query(sql)
            if is_valid:
                return sql, params
            else:
                self.logger.warning(f"Security check failed for generated SQL: {error}")
        except Exception as e:
            self.logger.warning(f"Error filling template: {str(e)}")

        return None, {}

    def explain_query(self, sql: str) -> str:
        """
        Generate a human-readable explanation of a SQL query.

        Args:
            sql: The SQL query to explain

        Returns:
            A natural language explanation of what the query does
        """
        # Simple rule-based explanation
        explanation = "This query "

        # Extract key parts of the query
        sql_lower = sql.lower()
        if sql_lower.startswith("select "):
            # Select query
            if "count(*)" in sql_lower:
                explanation += "counts the total number of records "
            elif " count(" in sql_lower:
                explanation += "counts records "
            elif " sum(" in sql_lower:
                explanation += "calculates the sum of a column "
            elif " avg(" in sql_lower:
                explanation += "calculates the average value of a column "
            elif " min(" in sql_lower:
                explanation += "finds the minimum value of a column "
            elif " max(" in sql_lower:
                explanation += "finds the maximum value of a column "
            elif " * " in sql_lower:
                explanation += "retrieves all columns from records "
            else:
                explanation += "retrieves specific columns from records "

            # From which table
            from_match = re.search(r"from\s+([^\s,]+)", sql_lower)
            if from_match:
                table = from_match.group(1)
                explanation += f"in the '{table}' table"

            # Where condition
            where_match = re.search(r"where\s+(.+?)(?:$|\s+(?:group|order|limit))", sql_lower)
            if where_match:
                condition = where_match.group(1)
                explanation += f" where {condition}"

            # Group by
            group_match = re.search(r"group\s+by\s+(.+?)(?:$|\s+(?:having|order|limit))", sql_lower)
            if group_match:
                grouping = group_match.group(1)
                explanation += f", grouped by {grouping}"

            # Order by
            order_match = re.search(r"order\s+by\s+(.+?)(?:$|\s+(?:limit))", sql_lower)
            if order_match:
                ordering = order_match.group(1)
                if "desc" in ordering.lower():
                    explanation += f", sorted in descending order by {ordering.replace('desc', '').strip()}"
                else:
                    explanation += f", sorted by {ordering}"

            # Limit
            limit_match = re.search(r"limit\s+(\d+)", sql_lower)
            if limit_match:
                limit = limit_match.group(1)
                explanation += f", limited to {limit} results"

        elif sql_lower.startswith("insert "):
            explanation = "This query inserts new records into a table"
        elif sql_lower.startswith("update "):
            explanation = "This query updates existing records in a table"
        elif sql_lower.startswith("delete "):
            explanation = "This query deletes records from a table"
        else:
            explanation = "This is a SQL query that performs a database operation"

        return explanation


def get_sql_generator(security_level: SecurityLevel = SecurityLevel.HIGH) -> SQLGenerator:
    """
    Get a default SQL generator instance.

    Args:
        security_level: Security level for generated queries

    Returns:
        A configured SQLGenerator instance
    """
    return SQLGenerator(security_level=security_level)


def generate_sql_from_text(
    natural_query: str,
    available_tables: List[str],
    available_columns: Optional[Dict[str, List[str]]] = None,
    security_level: SecurityLevel = SecurityLevel.HIGH,
) -> Tuple[str, Dict[str, Any]]:
    """
    Helper function to quickly generate SQL from natural language.

    Args:
        natural_query: The natural language query
        available_tables: List of available table names
        available_columns: Dictionary mapping table names to column lists
        security_level: Security level for generated queries

    Returns:
        A tuple of (sql_query, parameters)
    """
    generator = get_sql_generator(security_level)
    return generator.generate_sql(natural_query, available_tables, available_columns)
