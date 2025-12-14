import sqlite3
from typing import Any, Iterable

class DatabaseManager:
    """Handles SQLite database connections and queries."""
    # Initializes the objects
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None

    # Connect
    def connect(self) -> None:
        """Connects to the SQLite database."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)

    # Close
    def close(self) -> None:
        """Closes the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    # Execute query
    def execute_query(self, sql: str, params: Iterable[Any] = ()):
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        if self._connection is None:
            self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        self._connection.commit()
        return cur

    # Fetch one
    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        """Collect one row from a database."""
        # Check if the database is connected
        if self._connection is None:
            self.connect()
        # Fetches the data
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()

    # Fetch all
    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        """Collect all rows from a database."""
        # Check if the database is connected
        if self._connection is None:
            self.connect()
        # Fetches the data
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()