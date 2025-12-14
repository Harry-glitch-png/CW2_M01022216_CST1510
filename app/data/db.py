import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Root of project
DATA_DIR = BASE_DIR / "data" /"DATA"
DB_PATH = DATA_DIR / "intelligence_platform.db"

# Connect database
def connect_database(db_path=DB_PATH):
    """Connect to SQLite database."""
    return sqlite3.connect(str(db_path))