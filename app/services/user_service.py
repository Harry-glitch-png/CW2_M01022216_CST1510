import bcrypt
from pathlib import Path
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user
from app.data.schema import create_users_table
import pandas as pd
import sqlite3
from app.config import DATA_DIR, DB_PATH
from app.data.auth import *

# Register user
def register_user(username, password, role="user"):
    """
    Register a new user in the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        username: User's login name
        password: Plain text password (will be hashed)
        role: User role (default: 'user')

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    # Hash the password
    success, msg = validate_password(password)
    if success:
        password_hash = hash_password(password)
    else:
        return success, msg

    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit() # Save inserted data
    conn.close()

    return True, f"User '{username}' registered successfully!"

# Login user
def login_user(username, password):
    """
    Authenticate a user against the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        username: User's login name
        password: Plain text password to verify

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = connect_database()
    cursor = conn.cursor()

    # Find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "Username not found."

    # Verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."

# Migrate users from file
def migrate_users_from_file(conn, filepath=DATA_DIR / "users.txt"):
    """
    Migrate users from users.txt to the database.

    This is a COMPLETE IMPLEMENTATION as an example.

    Args:
        conn: Database connection
        filepath: Path to users.txt file
    """
    # Checks the file path
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        print("   No users to migrate.")
        return

    cursor = conn.cursor()
    migrated_count = 0

    # Gathers the data from the text file
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse line: username,password_hash
            parts = line.split(',')
            if len(parts) >= 2:
                username = parts[0]
                password_hash = parts[1]

                # Insert user (ignore if already exists)
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, 'user')
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.Error as e:
                    print(f"Error migrating user {username}: {e}")

    conn.commit() # Save inserted data
    # Varify that the data is migrated
    print(f"✅ Migrated {migrated_count} users from {filepath.name}")

# Load CSV to table
def load_csv_to_table(conn, csv_path, table_name):
    """
    Load a CSV file into a database table using pandas.


    Args:
        conn: Database connection
        csv_path: Path to CSV file
        table_name: Name of the target table

    Returns:
        int: Number of rows loaded
    """
    # Checks the path
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return

    # Read CSV into DataFrame
    df = pd.read_csv(csv_path)

    # Read existing rows
    existing = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

    # Merge and keep only new rows
    new_rows = df.merge(existing, how="left", indicator=True)
    new_rows = new_rows[new_rows["_merge"] == "left_only"].drop(columns=["_merge"])

    # Bulk insert all new rows
    if not new_rows.empty:
        new_rows.to_sql(table_name, conn, if_exists="append", index=False)
        print("Data loaded successfully")
    else:
        print("No new data to load")

    # Count rows in database
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Loaded {count} rows")
    return count