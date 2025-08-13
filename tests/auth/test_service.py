from unittest.mock import patch, MagicMock
from auth.service import (
    insert_user,
    get_user,
    update_user,
    delete_user,
    login_user,
    add_read_book,
    get_user_read_books
)
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


@patch("auth.service.oracledb.connect")
def test_add_read_book_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user found and book found
    mock_cursor.fetchone.side_effect = [
        (42,),  # user_id
        (99,)   # book_id
    ]

    add_read_book("dsn", "user", "pw", "alice", "Book Title", rating=5)

    # Check user_id query
    mock_cursor.execute.assert_any_call("SELECT user_id FROM users WHERE username = :1", ("alice",))
    # Check book_id query
    mock_cursor.execute.assert_any_call("SELECT book_id FROM books WHERE title = :1", ("Book Title",))
    # Check MERGE statement
    merge_args = mock_cursor.execute.call_args_list[-1][0]
    assert "MERGE INTO user_read_books ur" in merge_args[0]
    assert merge_args[1]["user_id"] == 42
    assert merge_args[1]["book_id"] == 99
    assert merge_args[1]["rating"] == 5
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_add_read_book_user_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user not found
    mock_cursor.fetchone.side_effect = [
        None  # user_id
    ]

    try:
        add_read_book("dsn", "user", "pw", "bob", "Book Title")
    except Exception as e:
        assert str(e) == "User not found"
    else:
        assert False, "Exception not raised for missing user"
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_add_read_book_book_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user found, book not found
    mock_cursor.fetchone.side_effect = [
        (42,),  # user_id
        None    # book_id
    ]

    try:
        add_read_book("dsn", "user", "pw", "alice", "Missing Book")
    except Exception as e:
        assert "not included in our DB" in str(e)
    else:
        assert False, "Exception not raised for missing book"
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect", side_effect=Exception("DB error"))
def test_add_read_book_db_error(mock_connect, capsys):
    try:
        add_read_book("dsn", "user", "pw", "alice", "Book Title")
    except Exception as e:
        assert str(e) == "DB error"
        captured = capsys.readouterr()
        assert "Failed to add read book: DB error" in captured.out
    else:
        assert False, "Exception not raised for DB error"


@patch("auth.service.oracledb.connect")
def test_get_user_read_books_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user found
    mock_cursor.fetchone.side_effect = [
        (42,)  # user_id
    ]
    # Simulate books read
    mock_cursor.fetchall.return_value = [
        ("Book A", 5, MagicMock(strftime=lambda fmt: "2023-01-01")),
        ("Book B", None, None),
        ("Book C", 3, MagicMock(strftime=lambda fmt: "2022-12-31"))
    ]

    books = get_user_read_books("dsn", "user", "pw", "alice")
    assert books == [
        {"title": "Book A", "rating": 5, "read_date": "2023-01-01"},
        {"title": "Book B", "rating": None, "read_date": None},
        {"title": "Book C", "rating": 3, "read_date": "2022-12-31"}
    ]
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_get_user_read_books_user_not_found(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user not found
    mock_cursor.fetchone.return_value = None

    books = get_user_read_books("dsn", "user", "pw", "bob")
    assert books == []
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect")
def test_get_user_read_books_no_books(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simulate user found
    mock_cursor.fetchone.side_effect = [
        (42,)  # user_id
    ]
    # Simulate no books read
    mock_cursor.fetchall.return_value = []

    books = get_user_read_books("dsn", "user", "pw", "alice")
    assert books == []
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("auth.service.oracledb.connect", side_effect=Exception("DB error"))
def test_get_user_read_books_db_error(mock_connect, capsys):
    books = get_user_read_books("dsn", "user", "pw", "alice")
    assert books == []
    captured = capsys.readouterr()
    assert "Failed to get user read books: DB error" in captured.out

@patch("auth.service.oracledb.connect")
def test_get_user_read_books_exception_in_fetchall(mock_connect, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.side_effect = [
        (42,)
    ]
    # Simulate exception in fetchall
    mock_cursor.fetchall.side_effect = Exception("Fetchall error")

    books = get_user_read_books("dsn", "user", "pw", "alice")
    assert books == []
    captured = capsys.readouterr()
    assert "Failed to get user read books: Fetchall error" in captured.out
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
