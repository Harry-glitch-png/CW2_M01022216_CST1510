from typing import Optional
from my_app.models.user import User
from my_app.services.database_manager import DatabaseManager
import bcrypt

class SimpleHasher:
    """Very basic hasher using SHA256 (for demo only)."""

    @staticmethod
    def hash_password(plain: str) -> str:
        """Hashes the password using"""
        password_bytes = plain.encode("utf-8")
        salt = bcrypt.gensalt(rounds=10) # Uses salt for extra security
        hashed = (bcrypt.hashpw(password_bytes, salt)).decode("utf-8")
        return hashed

    @staticmethod
    def check_password(plain: str, hashed: str) -> bool:
        """Checks if the password is correct"""
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8")) # Compares user password against the stored hashed password

class AuthManager:
    """Handles user registration and login."""
    # Initializes the objects
    def __init__(self, db: DatabaseManager, hasher=SimpleHasher):
        self._db = db
        self._hasher = hasher

    # Register user
    def register_user(self, username: str, password: str, role: str = "user") -> tuple[bool, str]:
        """Register a user in the database."""

        # Check if user already exists
        existing = self._db.fetch_one("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
        if existing:
            return False, f"Username '{username}' already exists."

        # --- Validate username ---
        valid_username, msg_username = User.validate_username(username)
        if not valid_username:
            return False, msg_username

        # --- Validate password ---
        valid_password, msg_password = User.validate_password(password)
        if not valid_password:
            return False, msg_password

        # Hash the password
        password_hash = SimpleHasher.hash_password(password)

        # Insert new user
        self._db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )

        return True, f"User '{username}' registered successfully!"

    # Login user
    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user against the database and allows the user to login.
        """
        # Find user
        row = self._db.fetch_one("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
        if row is None:
            return False, "Username not found."

        # row = (username, password_hash, role)
        username_db, password_hash_db, role_db = row

        # Create a User object
        user = User(username_db, password_hash_db, role_db)

        # Delegate verification to User.verify_password
        if user.verify_password(password, self._hasher):
            return True, f"Welcome, {username_db}!"
        else:
            return False, "Invalid password."