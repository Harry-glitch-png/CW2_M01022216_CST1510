import re

class User:
    """Represents a user in the Multi-Domain Intelligence Platform."""
    # Initializes the objects
    def __init__(self, username: str, password_hash: str, role: str):
        self.__username = username
        self.__password_hash = password_hash
        self.__role = role

    # Get username
    def get_username(self) -> str:
        """Return the username."""
        return self.__username

    # Get role
    def get_role(self) -> str:
        """Return the role."""
        return self.__role

    # Verify password
    def verify_password(self, plain_password: str, hasher) -> bool:
        """Check if a plain-text password matches this user's hash.
        `hasher` is any object with a `check_password(plain, hashed)` met
        """
        return hasher.check_password(plain_password, self.__password_hash)

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Check if a username is valid."""
        # Check username length
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        if len(username) > 20:
            return False, "Username must be at most 20 characters long."
        # Check username characters
        if re.search(r" ", username):
            return False, "There can be no spaces in your username."
        elif re.search(r"[a-zA-Z]", username):
            return True, "Valid username."
        return False, "The username must contain alphanumeric characters."

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Check if a password is valid."""
        # Check password length
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        if len(password) > 50:
            return False, "Password must be at most 50 characters long."
        # Check password characters
        if re.search(r" ", password):
            return False, "There can be no spaces in your password."
        elif (
            re.search(r"[a-z]", password)
            and re.search(r"[A-Z]", password)
            and re.search(r"\d", password)
            and re.search(r"[!@#$%^&*()_+=\-{}[\]:;\"'<>,.?/]", password)
        ):
            return True, "Valid password."
        return False, "Password must contain uppercase and lowercase letters, at least one number, and a special character."

    def __str__(self) -> str:
        return f"User({self.__username}, role={self.__role})"