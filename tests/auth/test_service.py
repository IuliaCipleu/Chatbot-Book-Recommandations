from unittest.mock import patch, MagicMock
from auth.service import insert_user, get_user, update_user, delete_user, login_user

@patch("auth.service.oracledb.connect")
@patch("auth.service.hash_password")
def test_insert_user_success(mock_hash_password, mock_connect):
    # Arrange
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_hash_password.return_value = "hashed_pw"

    # Act
    insert_user(
        conn_string="localhost/orclpdb1",
        db_user="chatbot_user",
        db_password="yourStrongPassword123",
        username="alice",
        email="alice@endava.com",
        plain_password="Password123!",
        language="english",
        profile="teen",
        voice_enabled=True
    )

    # Assert
    mock_connect.assert_called_once_with(
        user="chatbot_user",
        password="yourStrongPassword123",
        dsn="localhost/orclpdb1"
    )
    mock_conn.cursor.assert_called_once()
    mock_hash_password.assert_called_once_with("Password123!")
    mock_cursor.execute.assert_called_once_with(
        """
            INSERT INTO users (username, email, password_hash, language, profile, voice_enabled)
            VALUES (:1, :2, :3, :4, :5, :6)
        """,
        ("alice", "alice@endava.com", "hashed_pw", "english", "teen", "Y")
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
@patch("auth.service.hash_password")
def test_insert_user_voice_disabled(mock_hash_password, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_hash_password.return_value = "hashed_pw"

    insert_user(
        conn_string="localhost/orclpdb1",
        db_user="chatbot_user",
        db_password="yourStrongPassword123",
        username="bob",
        email="bob@endava.com",
        plain_password="Secret456!",
        language="romanian",
        profile="adult",
        voice_enabled=False
    )

    mock_cursor.execute.assert_called_once_with(
        """
            INSERT INTO users (username, email, password_hash, language, profile, voice_enabled)
            VALUES (:1, :2, :3, :4, :5, :6)
        """,
        ("bob", "bob@endava.com", "hashed_pw", "romanian", "adult", "N")
    )

@patch("auth.service.oracledb.connect", side_effect=Exception("DB error"))
@patch("auth.service.hash_password")
def test_insert_user_db_exception(mock_hash_password, mock_connect, capsys):
    # Should print error and not raise
    insert_user(
        conn_string="bad/conn",
        db_user="user",
        db_password="pw",
        username="fail",
        email="fail@endava.com",
        plain_password="fail",
        language="english",
        profile="adult",
        voice_enabled=False
    )
    captured = capsys.readouterr()
    assert "Failed to insert user: DB error" in captured.out


@patch("auth.service.oracledb.connect")
def test_get_user_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (
        "alice", "alice@endava.com", "english", "teen", "Y"
    )
    user = get_user("dsn", "user", "pw", "alice")
    assert user == {
        "username": "alice",
        "email": "alice@endava.com",
        "language": "english",
        "profile": "teen",
        "voice_enabled": True
    }
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_get_user_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    user = get_user("dsn", "user", "pw", "bob")
    assert user is None

@patch("auth.service.oracledb.connect")
def test_update_user_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    update_user(
        "dsn", "user", "pw", "alice",
        email="alice2@endava.com", language="romanian", profile="adult", voice_enabled=False
    )
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_update_user_no_fields(mock_connect, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    update_user("dsn", "user", "pw", "alice")
    captured = capsys.readouterr()
    assert "No fields to update." in captured.out

@patch("auth.service.oracledb.connect")
def test_delete_user_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    delete_user("dsn", "user", "pw", "alice")
    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM users WHERE username = :1", ("alice",)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
@patch("auth.service.verify_password")
def test_login_user_success(mock_verify_password, mock_connect, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (
        "hashed_pw", "alice@endava.com", "english", "teen", "Y"
    )
    mock_verify_password.return_value = True
    user = login_user("dsn", "user", "pw", "alice", "Password123!")
    # If login_user returns None, print output and fetched row for debugging
    if user is None:
        captured = capsys.readouterr()
        print("Captured output:", captured.out)
        print("Fetched row:", mock_cursor.fetchone.return_value)
    assert user is not None
    assert user["username"] == "alice"
    assert user["email"] == "alice@endava.com"
    assert user["language"] == "english"
    assert user["profile"] == "teen"
    assert user["voice_enabled"] is True
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
@patch("auth.service.verify_password")  # <-- patch here, not auth.encrypt.verify_password
def test_login_user_invalid_password(mock_verify_password, mock_connect, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (
        "hashed_pw", "alice@endava.com", "english", "teen", "Y"
    )
    mock_verify_password.return_value = False
    user = login_user("dsn", "user", "pw", "alice", "wrongpw")
    assert user is None
    captured = capsys.readouterr()
    assert ("Invalid password." in captured.out) or ("Login failed" in captured.out)

@patch("auth.service.oracledb.connect")
def test_login_user_not_found(mock_connect, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    user = login_user("dsn", "user", "pw", "bob", "pw")
    assert user is None
    captured = capsys.readouterr()
    assert "User not found." in captured.out
