"""
DataSpeak Connection Module

This module provides database connection management for DataSpeak, handling connections
to various database types, credentials, and query execution.
"""

import hashlib
import json
import logging
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import pandas as pd

try:
    import keyring

    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False
    logging.warning("keyring not found, secure credential storage will be limited")

# Import local modules
from plainspeak.plugins.dataspeak.security import SecurityLevel, SQLSecurityChecker, sanitize_and_check_query


class ConnectionError(Exception):
    """Exception raised for database connection issues."""


class QueryError(Exception):
    """Exception raised for query execution issues."""


class CredentialManager:
    """
    Handles secure storage and retrieval of database credentials.

    This class provides methods for securely storing and retrieving
    database connection credentials across sessions.
    """

    SERVICE_NAME = "plainspeak_dataspeak"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the credential manager.

        Args:
            config_path: Path to store encrypted credentials file if keyring is unavailable
        """
        self.logger = logging.getLogger("plainspeak.dataspeak.credentials")

        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".plainspeak" / "credentials"

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Secret key for encryption (when keyring not available)
        self._secret_key = None

    def store_credentials(self, connection_name: str, credentials: Dict[str, Any]) -> bool:
        """
        Store credentials securely.

        Args:
            connection_name: Unique name for this connection
            credentials: Dictionary containing connection credentials

        Returns:
            True if successful, False otherwise
        """
        try:
            if HAS_KEYRING:
                # Use system keyring
                keyring.set_password(self.SERVICE_NAME, connection_name, json.dumps(credentials))
            else:
                # Fallback to file-based storage with simple encryption
                if not self._secret_key:
                    self._load_or_create_key()

                encrypted = self._encrypt(json.dumps(credentials))
                self._save_to_file(connection_name, encrypted)

            return True
        except Exception as e:
            self.logger.error(f"Error storing credentials: {str(e)}")
            return False

    def get_credentials(self, connection_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored credentials.

        Args:
            connection_name: Unique name for the connection

        Returns:
            Dictionary containing connection credentials or None if not found
        """
        try:
            if HAS_KEYRING:
                # Use system keyring
                cred_json = keyring.get_password(self.SERVICE_NAME, connection_name)
                if not cred_json:
                    return None
                return json.loads(cred_json)
            else:
                # Fallback to file-based storage
                if not self._secret_key:
                    self._load_or_create_key()

                encrypted = self._load_from_file(connection_name)
                if not encrypted:
                    return None

                cred_json = self._decrypt(encrypted)
                return json.loads(cred_json)
        except Exception as e:
            self.logger.error(f"Error retrieving credentials: {str(e)}")
            return None

    def delete_credentials(self, connection_name: str) -> bool:
        """
        Delete stored credentials.

        Args:
            connection_name: Unique name for the connection

        Returns:
            True if successful, False otherwise
        """
        try:
            if HAS_KEYRING:
                # Use system keyring
                keyring.delete_password(self.SERVICE_NAME, connection_name)
            else:
                # Delete from file storage
                cred_file = self.config_path / f"{connection_name}.enc"
                if cred_file.exists():
                    cred_file.unlink()

            return True
        except Exception as e:
            self.logger.error(f"Error deleting credentials: {str(e)}")
            return False

    def list_connections(self) -> List[str]:
        """
        List all stored connection names.

        Returns:
            List of connection names
        """
        if HAS_KEYRING:
            # This is a limitation - keyring doesn't provide a way to list all keys
            # So we maintain a special meta-entry that lists all connections
            try:
                meta = keyring.get_password(self.SERVICE_NAME, "_connections")
                if meta:
                    return json.loads(meta)
                return []
            except Exception:
                return []
        else:
            # List files in the config directory
            try:
                connections = []
                if self.config_path.exists():
                    for file in self.config_path.glob("*.enc"):
                        conn_name = file.stem
                        if conn_name != "_key":
                            connections.append(conn_name)
                return connections
            except Exception:
                return []

    def _load_or_create_key(self):
        """Load or create the encryption key for file-based storage."""
        key_file = self.config_path / "_key.enc"

        if key_file.exists():
            with open(key_file, "rb") as f:
                self._secret_key = f.read()
        else:
            # Generate a new key
            self._secret_key = secrets.token_bytes(32)  # 256-bit key

            # Save the key
            with open(key_file, "wb") as f:
                f.write(self._secret_key)

            # Set secure permissions
            try:
                os.chmod(key_file, 0o600)  # Only owner can read/write
            except Exception:
                self.logger.warning("Could not set secure permissions on key file")

    def _encrypt(self, data: str) -> bytes:
        """
        Simple encryption function for file-based storage.

        Note: This is a basic implementation and not suitable for highly sensitive data.
        For better security, use the keyring backend.
        """
        # For simplicity, using a basic XOR cipher
        # In a real implementation, use a proper encryption library like cryptography
        data_bytes = data.encode("utf-8")
        key_bytes = self._secret_key

        # Create a deterministic but unique IV based on the data
        iv = hashlib.sha256(data_bytes[:32]).digest()[:16]

        # XOR encryption with key rotation
        encrypted = bytearray(len(data_bytes))
        for i in range(len(data_bytes)):
            key_idx = i % len(key_bytes)
            iv_idx = i % len(iv)
            encrypted[i] = data_bytes[i] ^ key_bytes[key_idx] ^ iv[iv_idx]

        return bytes(encrypted)

    def _decrypt(self, data: bytes) -> str:
        """
        Simple decryption function for file-based storage.

        See note in _encrypt method.
        """
        # Recreate the IV
        iv = hashlib.sha256(data[:32]).digest()[:16]

        # XOR decryption with key rotation
        decrypted = bytearray(len(data))
        for i in range(len(data)):
            key_idx = i % len(self._secret_key)
            iv_idx = i % len(iv)
            decrypted[i] = data[i] ^ self._secret_key[key_idx] ^ iv[iv_idx]

        return decrypted.decode("utf-8")

    def _save_to_file(self, connection_name: str, data: bytes):
        """Save encrypted data to file."""
        # Add to connections list
        connections = self.list_connections()
        if connection_name not in connections:
            connections.append(connection_name)

            # Save updated list
            meta_file = self.config_path / "_connections.json"
            with open(meta_file, "w") as f:
                json.dump(connections, f)

        # Save encrypted credentials
        cred_file = self.config_path / f"{connection_name}.enc"
        with open(cred_file, "wb") as f:
            f.write(data)

        # Set secure permissions
        try:
            os.chmod(cred_file, 0o600)  # Only owner can read/write
        except Exception:
            self.logger.warning("Could not set secure permissions on credential file")

    def _load_from_file(self, connection_name: str) -> Optional[bytes]:
        """Load encrypted data from file."""
        cred_file = self.config_path / f"{connection_name}.enc"
        if not cred_file.exists():
            return None

        with open(cred_file, "rb") as f:
            return f.read()


class DatabaseConnection:
    """
    Manages connections to various database types.

    This class provides a unified interface for connecting to different
    database systems and executing queries safely.
    """

    # Supported database types
    DB_TYPES = {
        "sqlite": "SQLite",
        "sqlite_memory": "SQLite In-Memory",
        "csv": "CSV Files",
    }

    def __init__(
        self,
        security_level: SecurityLevel = SecurityLevel.HIGH,
        credential_manager: Optional[CredentialManager] = None,
    ):
        """
        Initialize the database connection manager.

        Args:
            security_level: Security level for query execution
            credential_manager: Manager for secure credential storage
        """
        self.logger = logging.getLogger("plainspeak.dataspeak.connection")
        self.security_checker = SQLSecurityChecker(security_level)
        self.security_level = security_level

        # Initialize credential manager if not provided
        if credential_manager:
            self.credential_manager = credential_manager
        else:
            self.credential_manager = CredentialManager()

        # Connection pool for reuse
        self._connections: Dict[str, Dict[str, Any]] = {}

    def create_connection(
        self,
        connection_name: str,
        db_type: str,
        connection_params: Dict[str, Any],
        save_credentials: bool = False,
    ) -> bool:
        """
        Create a new database connection.

        Args:
            connection_name: Unique name for this connection
            db_type: Type of database (sqlite, sqlite_memory, csv)
            connection_params: Connection parameters specific to the database type
            save_credentials: Whether to save credentials for future sessions

        Returns:
            True if connection was successfully created, False otherwise
        """
        # Validate database type
        if db_type not in self.DB_TYPES:
            raise ValueError(f"Unsupported database type: {db_type}")

        conn: Any = None
        try:
            if db_type == "sqlite":
                # Required parameter: database_path
                if "database_path" not in connection_params:
                    raise ValueError("database_path is required for SQLite connections")

                db_path = connection_params["database_path"]
                conn = sqlite3.connect(db_path)

                # Configure SQLite connection
                conn.row_factory = sqlite3.Row

                # Test connection
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version()")
                cursor.close()

            elif db_type == "sqlite_memory":
                # In-memory SQLite database
                conn = sqlite3.connect(":memory:")
                conn.row_factory = sqlite3.Row

                # Test connection
                cursor = conn.cursor()
                cursor.execute("SELECT sqlite_version()")
                cursor.close()

            elif db_type == "csv":
                # Required parameter: data_directory
                if "data_directory" not in connection_params:
                    raise ValueError("data_directory is required for CSV connections")

                # Check if directory exists
                data_dir = Path(connection_params["data_directory"])
                if not data_dir.exists() or not data_dir.is_dir():
                    raise ValueError(f"Data directory does not exist: {data_dir}")

                # Create a dictionary to hold loaded dataframes
                conn = {"data_directory": data_dir, "dataframes": {}}

                # Preload CSV files if requested
                if connection_params.get("preload_files", False):
                    self._load_csv_files(conn)

            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            # Store connection
            self._connections[connection_name] = {
                "connection": conn,
                "db_type": db_type,
                "params": connection_params,
            }

            # Save credentials if requested
            if save_credentials:
                creds = {"db_type": db_type, "params": connection_params}
                self.credential_manager.store_credentials(connection_name, creds)

            return True

        except Exception as e:
            self.logger.error(f"Error creating connection '{connection_name}': {str(e)}")
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def load_connection(self, connection_name: str) -> bool:
        """
        Load a previously saved database connection.

        Args:
            connection_name: Unique name for the connection

        Returns:
            True if connection was successfully loaded, False otherwise
        """
        # Check if already connected
        if connection_name in self._connections:
            return True

        # Retrieve credentials
        creds = self.credential_manager.get_credentials(connection_name)
        if not creds:
            raise ConnectionError(f"No saved credentials found for '{connection_name}'")

        # Create connection with saved parameters
        db_type = creds["db_type"]
        params = creds["params"]

        return self.create_connection(connection_name, db_type, params, save_credentials=False)

    def close_connection(self, connection_name: str) -> bool:
        """
        Close a database connection.

        Args:
            connection_name: Unique name for the connection

        Returns:
            True if connection was closed, False otherwise
        """
        if connection_name not in self._connections:
            return False

        try:
            conn_info = self._connections[connection_name]
            if conn_info["db_type"] in ["sqlite", "sqlite_memory"]:
                conn_info["connection"].close()

            # Remove from pool
            del self._connections[connection_name]
            return True

        except Exception as e:
            self.logger.error(f"Error closing connection '{connection_name}': {str(e)}")
            return False

    def list_connections(self) -> List[str]:
        """
        List all active connections.

        Returns:
            List of active connection names
        """
        return list(self._connections.keys())

    def list_saved_connections(self) -> List[str]:
        """
        List all saved connections.

        Returns:
            List of saved connection names
        """
        return self.credential_manager.list_connections()

    @contextmanager
    def connection(self, connection_name: str) -> Iterator[Any]:
        """
        Context manager for database connections.

        Args:
            connection_name: Unique name for the connection

        Yields:
            Database connection object
        """
        if connection_name not in self._connections:
            # Try to load from saved connections
            if not self.load_connection(connection_name):
                raise ConnectionError(f"Connection '{connection_name}' not found")

        conn_info = self._connections[connection_name]
        conn = conn_info["connection"]

        try:
            yield conn
        finally:
            # For SQLite, we don't close the connection here to allow connection pooling
            pass

    @contextmanager
    def transaction(self, connection_name: str) -> Iterator[Any]:
        """
        Context manager for database transactions.

        Args:
            connection_name: Unique name for the connection

        Yields:
            Database connection object
        """
        if connection_name not in self._connections:
            raise ConnectionError(f"Connection '{connection_name}' not found")

        conn_info = self._connections[connection_name]
        conn = conn_info["connection"]
        db_type = conn_info["db_type"]

        if db_type in ["sqlite", "sqlite_memory"]:
            try:
                # For SQLite, we can use the connection as a context manager for transactions
                with conn:
                    yield conn
            except Exception as e:
                self.logger.error(f"Transaction error: {str(e)}")
                raise
        elif db_type == "csv":
            # CSV connections don't support transactions
            try:
                yield conn
            except Exception as e:
                self.logger.error(f"CSV operation error: {str(e)}")
                raise
        else:
            raise ConnectionError(f"Transactions not supported for {db_type}")

    def execute_query(
        self,
        connection_name: str,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch_all: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Optional[int]]:
        """
        Execute a SQL query safely.

        Args:
            connection_name: Unique name for the connection
            query: SQL query to execute
            params: Query parameters for safe parameterized queries
            fetch_all: Whether to fetch all results

        Returns:
            Tuple of (results, rowcount) where:
              - results is a list of dictionaries, one per row
              - rowcount is the number of rows affected (for DML statements)
        """
        if connection_name not in self._connections:
            raise ConnectionError(f"Connection '{connection_name}' not found")

        conn_info = self._connections[connection_name]
        db_type = conn_info["db_type"]

        # Sanitize and check query
        safe_query, _ = sanitize_and_check_query(query, params, self.security_level)

        # Execute query based on database type
        if db_type in ["sqlite", "sqlite_memory"]:
            return self._execute_sqlite_query(conn_info["connection"], safe_query, params, fetch_all)
        elif db_type == "csv":
            return self._execute_csv_query(conn_info["connection"], safe_query, params)
        else:
            raise ConnectionError(f"Queries not supported for {db_type}")

    def query_to_dataframe(
        self, connection_name: str, query: str, params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Execute a query and return results as a pandas DataFrame.

        Args:
            connection_name: Unique name for the connection
            query: SQL query to execute
            params: Query parameters for safe parameterized queries

        Returns:
            Pandas DataFrame containing query results
        """
        results, _ = self.execute_query(connection_name, query, params)
        return pd.DataFrame(results)

    def list_tables(self, connection_name: str) -> List[str]:
        """
        List all tables in the database.

        Args:
            connection_name: Unique name for the connection

        Returns:
            List of table names
        """
        if connection_name not in self._connections:
            raise ConnectionError(f"Connection '{connection_name}' not found")

        conn_info = self._connections[connection_name]
        db_type = conn_info["db_type"]

        if db_type in ["sqlite", "sqlite_memory"]:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            results, _ = self._execute_sqlite_query(conn_info["connection"], query, None, True)
            return [row["name"] for row in results if not row["name"].startswith("sqlite_")]
        elif db_type == "csv":
            # For CSV, return loaded dataframes
            conn = conn_info["connection"]

            # Load CSV files if not loaded yet
            if not conn["dataframes"]:
                self._load_csv_files(conn)

            return list(conn["dataframes"].keys())
        else:
            raise ConnectionError(f"Listing tables not supported for {db_type}")

    def get_table_schema(self, connection_name: str, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema for a table.

        Args:
            connection_name: Unique name for the connection
            table_name: Name of the table

        Returns:
            List of column definitions (name, type, etc.)
        """
        if connection_name not in self._connections:
            raise ConnectionError(f"Connection '{connection_name}' not found")

        conn_info = self._connections[connection_name]
        db_type = conn_info["db_type"]

        if db_type in ["sqlite", "sqlite_memory"]:
            query = f"PRAGMA table_info({table_name})"
            results, _ = self._execute_sqlite_query(conn_info["connection"], query, None, True)
            return results
        elif db_type == "csv":
            # For CSV, return the dtypes from pandas
            conn = conn_info["connection"]

            if table_name not in conn["dataframes"]:
                self._load_csv_files(conn)

            if table_name not in conn["dataframes"]:
                raise ValueError(f"CSV table {table_name} not found")

            df = conn["dataframes"][table_name]
            schema = []

            for col_name, dtype in df.dtypes.items():
                schema.append(
                    {
                        "name": col_name,
                        "type": str(dtype),
                        "notnull": 0 if df[col_name].isna().any() else 1,
                        "dflt_value": None,
                        "pk": 0,  # No primary key concept in CSV
                    }
                )

            return schema
        else:
            raise ConnectionError(f"Schema retrieval not supported for {db_type}")

    def _execute_sqlite_query(
        self,
        conn: sqlite3.Connection,
        query: str,
        params: Optional[Dict[str, Any]],
        fetch_all: bool,
    ) -> Tuple[List[Dict[str, Any]], Optional[int]]:
        """Execute a query on a SQLite connection."""
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get results for SELECT queries
            if query.strip().upper().startswith("SELECT"):
                if fetch_all:
                    rows = cursor.fetchall()
                    result = [{k: row[k] for k in row.keys()} for row in rows]
                    return result, cursor.rowcount
                else:
                    row = cursor.fetchone()
                    if row:
                        result = [{k: row[k] for k in row.keys()}]
                        return result, 1
                    else:
                        return [], 0
            else:
                # For non-SELECT queries, return empty results with rowcount
                return [], cursor.rowcount

        finally:
            cursor.close()

    def _execute_csv_query(
        self, conn: Dict[str, Any], query: str, params: Optional[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], None]:
        """Execute a query on CSV files using pandas."""
        # Simple CSV querying via pandas
        # This is a very limited implementation that only supports basic filtering

        # Load CSV files if not loaded yet
        if not conn["dataframes"]:
            self._load_csv_files(conn)

        # Parse the query
        # This is a very simple parser for demonstration purposes
        # In a real implementation, you would use a proper SQL parser
        query = query.strip().lower()

        if query.startswith("select "):
            # Extract table name from FROM clause
            match = re.search(r"from\s+(\w+)", query)
            if not match:
                raise QueryError("Could not find table name in FROM clause")

            table_name = match.group(1)

            if table_name not in conn["dataframes"]:
                raise QueryError(f"Table {table_name} not found")

            df = conn["dataframes"][table_name]

            # Handle WHERE clause
            where_match = re.search(r"where\s+(.+?)(?:$|order\s+by|limit)", query)
            if where_match:
                # Very simple WHERE clause parsing
                # Only handles single conditions with =, >, <
                condition = where_match.group(1).strip()

                # Replace parameters
                if params:
                    for param, value in params.items():
                        condition = condition.replace(f":{param}", repr(value))

                # Parse the condition
                # This is extremely primitive and only handles simple conditions
                if "=" in condition:
                    col, val = condition.split("=", 1)
                    col = col.strip()
                    val = eval(val.strip())  # DANGER: never do this in production
                    df = df[df[col] == val]
                elif ">" in condition:
                    col, val = condition.split(">", 1)
                    col = col.strip()
                    val = eval(val.strip())
                    df = df[df[col] > val]
                elif "<" in condition:
                    col, val = condition.split("<", 1)
                    col = col.strip()
                    val = eval(val.strip())
                    df = df[df[col] < val]

            # Handle LIMIT clause
            limit_match = re.search(r"limit\s+(\d+)", query)
            if limit_match:
                limit = int(limit_match.group(1))
                df = df.head(limit)

            # Convert to list of dicts
            result = df.to_dict(orient="records")
            return result, None
        else:
            raise QueryError("Only SELECT queries are supported for CSV files")

    def _load_csv_files(self, conn: Dict[str, Any]):
        """Load CSV files from the data directory."""
        data_dir = conn["data_directory"]

        for file in data_dir.glob("*.csv"):
            table_name = file.stem
            try:
                df = pd.read_csv(file)
                conn["dataframes"][table_name] = df
            except Exception as e:
                self.logger.warning(f"Error loading CSV file {file}: {str(e)}")


def get_default_connection() -> DatabaseConnection:
    """
    Get a default database connection instance.

    Returns:
        A configured DatabaseConnection instance
    """
    return DatabaseConnection(security_level=SecurityLevel.HIGH)


def execute_query(
    connection_name: str,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    security_level: SecurityLevel = SecurityLevel.HIGH,
) -> pd.DataFrame:
    """
    Helper function to quickly execute a query.

    Args:
        connection_name: Name of the connection to use
        query: SQL query to execute
        params: Query parameters for safe parameterized queries
        security_level: Security level for query execution

    Returns:
        Pandas DataFrame containing query results
    """
    db = get_default_connection()
    if connection_name not in db.list_connections():
        db.load_connection(connection_name)

    return db.query_to_dataframe(connection_name, query, params)
