"""
Password hashing and verification utilities using bcrypt.
Functions:
- hash_password: Hashes a password using bcrypt.
- verify_password: Verifies a password against a bcrypt hash.
"""
import bcrypt

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Args:
        password (str): The plaintext password to hash.
    Returns:
        str: The bcrypt hash of the password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hash: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    Args:
        password (str): The plaintext password to verify.
        hash (str): The bcrypt hash to check against.
    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    try:
        return bcrypt.checkpw(password.encode(), hash.encode())
    except Exception:
        return False
