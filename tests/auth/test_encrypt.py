"""
Unit tests for password hashing and verification functions in auth.encrypt.
Tests included:
- test_hash_password_returns_str: Ensures hash_password returns a string with a valid bcrypt prefix.
- test_verify_password_correct: Checks that verify_password returns True for correct password.
- test_verify_password_incorrect: Checks that verify_password returns False for incorrect password.
- test_hash_password_unique_salt: Verifies that hashing the same password twice yields different hashes due to unique salts.
- test_verify_password_empty_string: Tests hashing and verifying empty string passwords.
- test_verify_password_invalid_hash: Ensures verify_password returns False for invalid hash formats.
- test_hash_password_unicode: Tests hashing and verifying passwords with Unicode characters.
"""
from auth.encrypt import hash_password, verify_password

def test_hash_password_returns_str():
    pw = "MySecret123!"
    hashed = hash_password(pw)
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$")

def test_verify_password_correct():
    pw = "AnotherSecret!"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True

def test_verify_password_incorrect():
    pw = "Password1"
    wrong_pw = "Password2"
    hashed = hash_password(pw)
    assert verify_password(wrong_pw, hashed) is False

def test_hash_password_unique_salt():
    pw = "SamePassword"
    h1 = hash_password(pw)
    h2 = hash_password(pw)
    assert h1 != h2  # Salts should make hashes different

def test_verify_password_empty_string():
    hashed = hash_password("")
    assert verify_password("", hashed) is True
    assert verify_password("notempty", hashed) is False

def test_verify_password_invalid_hash():
    # Should not raise, just return False
    assert verify_password("pw", "not_a_bcrypt_hash") is False

def test_hash_password_unicode():
    pw = "pässwördÜñîçødë"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed) is True
    assert verify_password("pässwördÜñîçødë_wrong", hashed) is False
