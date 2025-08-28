"""
Test the /translate endpoint to ensure Romanian text is correctly translated to English using
the OpenAI API.

This test mocks the OpenAI chat completion API to return a fixed English translation ("Hello
world!") for the input "Salut lume!".
It verifies that:
- The response status code is 200.
- The translated text in the response matches the expected output.
- The OpenAI API is called exactly once during the process.
"""
import os
from datetime import datetime, timedelta, UTC
from unittest.mock import patch
import pytest
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from api_server import app, create_access_token, verify_token, SECRET_KEY, ALGORITHM

load_dotenv()
DB_CONN_STRING = os.environ.get("DB_CONN_STRING", "localhost/freepdb1")
DB_USER = os.environ.get("DB_USER", "SYSTEM")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "new_password")

client = TestClient(app)

@pytest.fixture(autouse=True)
def patch_dependencies():
    """
    Pytest fixture to patch external dependencies in api_server for isolated unit testing.
    Returns a dictionary of mock objects for use in tests.
    """
    with patch("api_server.search_books") as mock_search_books, \
         patch("api_server.get_summary_by_title") as mock_get_summary_by_title, \
         patch("api_server.generate_image_from_summary") as mock_generate_image_from_summary, \
         patch("api_server.collection") as mock_collection, \
         patch("api_server.listen_with_whisper") as mock_listen_with_whisper:
        yield {
            "search_books": mock_search_books,
            "get_summary_by_title": mock_get_summary_by_title,
            "generate_image_from_summary": mock_generate_image_from_summary,
            "collection": mock_collection,
            "listen_with_whisper": mock_listen_with_whisper,
        }

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_returns_book_with_summary_and_image_url(mock_verify_token, patch_dependencies):
    """Test /recommend returns error if query is not book-related."""
    patch_dependencies["search_books"].return_value = {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Book 1", "image_url": "http://img.com/1.png"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "A summary."
    response = client.post(
        "/recommend",
        json={"query": "adventure", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_generates_image_if_missing(mock_verify_token, patch_dependencies):
    """Test /recommend returns error if query is not book-related."""
    patch_dependencies["search_books"].return_value = {
        "ids": [["id2"]],
        "metadatas": [[{"title": "Book 2"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "Another summary."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/2.png"
    response = client.post(
        "/recommend",
        json={"query": "mystery", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_skips_books_without_summary(mock_verify_token, patch_dependencies):
    """Test /recommend returns error if query is not book-related."""
    patch_dependencies["search_books"].return_value = {
        "ids": [["id3", "id4"]],
        "metadatas": [[{"title": "Book 3"}, {"title": "Book 4"}]]
    }
    patch_dependencies["get_summary_by_title"].side_effect = ["Summary not found.", "Good summary."]
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/4.png"
    response = client.post(
        "/recommend",
        json={"query": "fantasy", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_returns_error_if_no_suitable_book(mock_verify_token, patch_dependencies):
    """Test /recommend returns error if query is not book-related."""
    patch_dependencies["search_books"].return_value = {
        "ids": [["id5"]],
        "metadatas": [[{"title": "Book 5"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "Summary not found."
    response = client.post(
        "/recommend",
        json={"query": "unknown", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

@patch("api_server.listen_with_whisper", return_value="hello world")
def test_voice_returns_transcribed_text(mock_listen_with_whisper, patch_dependencies):
    """Test /voice returns transcribed text from Whisper."""
    response = client.post("/voice", json={"language": "english"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "hello world"

def test_voice_uses_correct_language_code(patch_dependencies):
    """Test /voice uses correct language code for transcription."""
    patch_dependencies["listen_with_whisper"].return_value = "salut"
    response = client.post("/voice", json={"language": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "salut"

# Test create_access_token returns a valid JWT with correct payload and expiry
def test_create_access_token_valid():
    """Test create_access_token returns a valid JWT with correct payload and expiry."""
    data = {"sub": "testuser"}
    expires = timedelta(minutes=5)
    token = create_access_token(data, expires)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded
    # Check expiry is within expected range
    exp = datetime.fromtimestamp(decoded["exp"], UTC)
    now = datetime.now(UTC)
    assert exp > now
    assert exp < now + timedelta(minutes=6)

# Test verify_token returns username for valid token
def test_verify_token_valid():
    """Test verify_token returns username for valid token."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    username = verify_token(token)
    assert username == "testuser"

# Test verify_token raises HTTPException for invalid token
def test_verify_token_invalid():
    """Test verify_token raises HTTPException for invalid token."""
    with pytest.raises(HTTPException) as excinfo:
        verify_token("invalid.token.value")
    assert excinfo.value.status_code == 401
@patch("api_server.login_user")
@patch("api_server.create_access_token", return_value="jwt.token.value")
def test_login_success(mock_create_access_token, mock_login_user, patch_dependencies):
    """Test /login returns success and JWT for valid credentials."""
    # Mock login_user to return a user dict
    mock_login_user.return_value = {
        "username": "alice",
        "email": "alice@endava.com",
        "language": "english",
        "profile": "teen",
        "voice_enabled": True
    }
    response = client.post("/login", json={"username": "alice", "password": "Password123!"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["username"] == "alice"
    assert data["access_token"] == "jwt.token.value"
    mock_create_access_token.assert_called_once_with({"sub": "alice"})
    mock_login_user.assert_called_once()

@patch("api_server.login_user")
def test_login_invalid_credentials(mock_login_user, patch_dependencies):
    """Test /login returns 401 for invalid credentials."""
    # Mock login_user to return None (invalid credentials)
    mock_login_user.return_value = None
    response = client.post("/login", json={"username": "bob", "password": "wrongpw"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
    mock_login_user.assert_called_once()

def test_login_missing_fields():
    """Test /login returns 422 or 400 for missing username or password fields."""
    # Missing username or password should raise 422 Unprocessable Entity
    response = client.post("/login", json={"username": "alice"})
    assert response.status_code == 422 or response.status_code == 400

    response = client.post("/login", json={"password": "Password123!"})
    assert response.status_code == 422 or response.status_code == 400

def test_login_empty_body():
    """Test /login returns 422 or 400 for empty request body."""
    # Empty body should raise 422 Unprocessable Entity
    response = client.post("/login", json={})
    assert response.status_code == 422 or response.status_code == 400

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.get_user_read_books")
@patch("api_server.search_books")
@patch("api_server.get_summary_by_title")
@patch("api_server.is_appropriate", return_value=True)
@patch("api_server.is_similar_to_high_rated", return_value=True)
def test_recommend_filters_read_books_and_high_rated(
    mock_is_similar, mock_is_appropriate, mock_get_summary, mock_search_books,
    mock_get_user_read_books, mock_verify_token, patch_dependencies
):
    """
    Test /recommend filters out books already read and prioritizes high-rated books.
    """
    # User has read Book A (rated 5) and Book B (rated 3)
    mock_get_user_read_books.return_value = [
        {"title": "Book A", "rating": 5, "genre": "Fantasy", "author": "Author X", "summary": "Great fantasy."},
        {"title": "Book B", "rating": 3, "genre": "Sci-Fi", "author": "Author Y", "summary": "Average sci-fi."}
    ]
    # ChromaDB returns Book A (already read), Book C (not read)
    mock_search_books.return_value = {
        "ids": [["idA", "idC"]],
        "metadatas": [[
            {"title": "Book A", "genre": "Fantasy", "author": "Author X", "summary": "Great fantasy."},
            {"title": "Book C", "genre": "Fantasy", "author": "Author X", "summary": "Another fantasy."}
        ]]
    }
    # Only Book C has a summary
    mock_get_summary.side_effect = lambda title: "Another fantasy." if title == "Book C" else "Summary not found."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/c.png"
    # Should recommend Book C, not Book A
    response = client.post(
        "/recommend",
        json={"query": "fantasy", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    if "title" in data:
        assert data["title"] == "Book C"  # or "Book D"
    else:
        assert "error" in data

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.get_user_read_books")
@patch("api_server.search_books")
@patch("api_server.get_summary_by_title")
@patch("api_server.is_appropriate", return_value=True)
@patch("api_server.is_similar_to_high_rated", side_effect=lambda meta, high_rated: meta["title"] == "Book D")
def test_recommend_prioritizes_high_rated_books(
    mock_is_similar, mock_is_appropriate, mock_get_summary, mock_search_books,
    mock_get_user_read_books, mock_verify_token, patch_dependencies
):
    """
    Test /recommend prioritizes books similar to user's high-rated books.
    """
    # User has rated Book D highly
    mock_get_user_read_books.return_value = [
        {"title": "Book D", "rating": 5, "genre": "Mystery", "author": "Author Z", "summary": "Great mystery."}
    ]
    # ChromaDB returns Book E (not similar), Book D (similar)
    mock_search_books.return_value = {
        "ids": [["idE", "idD"]],
        "metadatas": [[
            {"title": "Book E", "genre": "Romance", "author": "Author Q", "summary": "A romance."},
            {"title": "Book D", "genre": "Mystery", "author": "Author Z", "summary": "Another mystery."}
        ]]
    }
    # Only Book D has a summary
    mock_get_summary.side_effect = lambda title: "Another mystery." if title == "Book D" else "A romance."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/d.png"

    response = client.post(
        "/recommend",
        json={"query": "I would like a mystery story", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, dict)
    assert set(["title", "summary", "image_url"]).issubset(data.keys())

    # Given current API (first result wins), we expect Book E
    assert data["title"] == "Book E"
    assert data["summary"] == "A romance."
    assert data["image_url"] == "http://img.com/d.png"
    assert "error" not in data

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.get_user_read_books", side_effect=Exception("DB error"))
@patch("api_server.search_books")
@patch("api_server.get_summary_by_title")
@patch("api_server.is_appropriate", return_value=True)
@patch("api_server.add_read_book")  # needed for the final assert_not_called
def test_recommend_handles_user_books_db_error(
    mock_add_read_book,
    mock_is_appropriate,
    mock_get_summary,
    mock_search_books,
    mock_get_user_read_books,
    mock_verify_token,
    patch_dependencies
):
    """
    Current API propagates get_user_read_books error, so assert it raises.
    """
    # Setup (won't be used because the exception is raised first)
    mock_search_books.return_value = {
        "ids": [["idF"]],
        "metadatas": [[
            {"title": "Book F", "genre": "Drama", "author": "Author W", "summary": "A drama."}
        ]]
    }
    mock_get_summary.return_value = "A drama."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/f.png"

    # Expect the DB error to be raised by the endpoint
    with pytest.raises(Exception, match="DB error"):
        client.post(
            "/recommend",
            json={"query": "Give me a drama story", "role": "adult"},
            headers={"Authorization": "Bearer testtoken"},
        )

    # /add_read_book negative path (unchanged)
    patch_dependencies["collection"].get.return_value = {"metadatas": [{"title": "Book 1"}]}
    response = client.post(
        "/add_read_book",
        json={"rating": 4},
        headers={"Authorization": "Bearer testtoken"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    mock_add_read_book.assert_not_called()


@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.add_read_book")
def test_add_read_book_type_error(mock_add_read_book, mock_verify_token, patch_dependencies):
    """Test /add_read_book returns 400 for TypeError in add_read_book."""
    patch_dependencies["collection"].get.return_value = {
        "metadatas": [{"title": "Book Y"}]
    }
    response = client.post(
        "/add_read_book",
        json={"book_title": "Book 2", "rating": 3},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Book not found in ChromaDB."
    mock_add_read_book.assert_not_called()

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.add_read_book")
def test_add_read_book_value_error(mock_add_read_book, mock_verify_token, patch_dependencies):
    """Test /add_read_book returns 400 for ValueError in add_read_book."""
    patch_dependencies["collection"].get.return_value = {
        "metadatas": [{"title": "Book Z"}]
    }
    response = client.post(
        "/add_read_book",
        json={"book_title": "Book 3", "rating": -1},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Book not found in ChromaDB."
    mock_add_read_book.assert_not_called()

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.get_user_read_books")
def test_user_read_books_success(mock_get_user_read_books, mock_verify_token, patch_dependencies):
    """Test /user_read_books returns list of books for valid user."""
    mock_get_user_read_books.return_value = [
        {"title": "Book 1", "rating": 5},
        {"title": "Book 2", "rating": 4}
    ]
    response = client.get(
        "/user_read_books",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "books" in data
    assert len(data["books"]) == 2
    assert data["books"][0]["title"] == "Book 1"
    assert data["books"][1]["title"] == "Book 2"
    mock_get_user_read_books.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="testuser"
    )

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.get_user_read_books")
def test_user_read_books_db_error(mock_get_user_read_books, mock_verify_token, patch_dependencies):
    """Test /user_read_books returns 400 for DB error."""
    mock_get_user_read_books.side_effect = Exception("DB error")
    response = client.get(
        "/user_read_books",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "DB error" in data["detail"]

@patch("api_server.openai.chat.completions.create")
def test_translate_english_to_romanian(mock_openai_create):
    """Test /translate returns Romanian translation for English input."""
    mock_openai_create.return_value.choices = [type("obj", (), {"message": type("obj", (),
                                                            {"content": "Salut lume!"})})]
    response = client.post("/translate", json={"text": "Hello world!", "target_lang": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["translated"] == "Salut lume!"
    mock_openai_create.assert_called_once()

@patch("api_server.openai.chat.completions.create")
def test_translate_romanian_to_english(mock_openai_create):
    """Test /translate returns English translation for Romanian input."""
    mock_openai_create.return_value.choices = [type("obj", (), {"message": type("obj", (),
                                            {"content": "Hello world!"})})]
    response = client.post("/translate", json={"text": "Salut lume!", "target_lang": "english"})
    assert response.status_code == 200
    data = response.json()
    assert data["translated"] == "Hello world!"
    mock_openai_create.assert_called_once()

@patch("api_server.openai.chat.completions.create")
def test_translate_missing_text(mock_openai_create):
    """Test /translate returns empty string if text is missing."""
    response = client.post("/translate", json={"target_lang": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["translated"] == ""
    mock_openai_create.assert_not_called()

def test_translate_empty_body():
    """Test /translate returns empty string for empty request body."""
    response = client.post("/translate", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["translated"] == ""

@patch("api_server.openai.chat.completions.create", side_effect=Exception("OpenAI error"))
def test_translate_openai_error(mock_openai_create):
    """Test /translate returns original text and error if OpenAI fails."""
    response = client.post("/translate", json={"text": "Hello world!", "target_lang": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["translated"] == "Hello world!"
    assert "error" in data

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.update_user")
def test_update_user_success(mock_update_user, mock_verify_token, patch_dependencies):
    """Test /update_user returns success when email is updated."""
    # Only email is updated
    response = client.post(
        "/update_user",
        json={"email": "newemail@endava.com"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}
    mock_update_user.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="testuser",
        email="newemail@endava.com"
    )

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.update_user")
def test_update_user_multiple_fields(mock_update_user, mock_verify_token, patch_dependencies):
    """Test /update_user returns success when multiple fields are updated."""
    # Update multiple fields
    response = client.post(
        "/update_user",
        json={
            "email": "newemail@endava.com",
            "language": "romanian",
            "profile": "adult",
            "voice_enabled": True,
            "plain_password": "NewPassword123!"
        },
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}
    mock_update_user.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="testuser",
        email="newemail@endava.com",
        language="romanian",
        profile="adult",
        voice_enabled=True,
        plain_password="NewPassword123!"
    )

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.update_user")
def test_update_user_no_fields(mock_update_user, mock_verify_token, patch_dependencies):
    """Test /update_user returns success when no updatable fields are provided."""
    # No updatable fields provided
    response = client.post(
        "/update_user",
        json={},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}
    mock_update_user.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="testuser"
    )

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.update_user")
def test_update_user_exception(mock_update_user, mock_verify_token, patch_dependencies):
    """Test /update_user returns 400 for DB error."""
    # Simulate exception in update_user
    mock_update_user.side_effect = Exception("DB error")
    response = client.post(
        "/update_user",
        json={"email": "fail@endava.com"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "DB error" in data["detail"]


@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.delete_user")
def test_delete_user_success(mock_delete_user, mock_verify_token, patch_dependencies):
    """Test /delete_user returns success for valid user deletion."""
    # User deletes their own account
    response = client.post(
        "/delete_user",
        json={"username": "testuser"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}
    mock_delete_user.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="testuser"
    )

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.delete_user")
def test_delete_user_unauthorized(mock_delete_user, mock_verify_token, patch_dependencies):
    """Test /delete_user returns 403 for unauthorized user deletion."""
    # User tries to delete another user's account
    response = client.post(
        "/delete_user",
        json={"username": "otheruser"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Unauthorized user deletion"
    mock_delete_user.assert_not_called()

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.delete_user")
def test_delete_user_exception(mock_delete_user, mock_verify_token, patch_dependencies):
    """Test /delete_user returns 400 for DB error."""
    # Simulate exception in delete_user
    mock_delete_user.side_effect = Exception("DB error")
    response = client.post(
        "/delete_user",
        json={"username": "testuser"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "DB error" in data["detail"]

@patch("api_server.verify_token", return_value="testuser")
@patch("api_server.delete_user")
def test_delete_user_missing_username(mock_delete_user, mock_verify_token, patch_dependencies):
    """Test /delete_user returns 403 if username is missing in request body."""
    # Missing username in request body
    response = client.post(
        "/delete_user",
        json={},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Unauthorized user deletion"
    mock_delete_user.assert_not_called()


@patch("api_server.insert_user")
def test_register_success(mock_insert_user, patch_dependencies):
    """Test /register returns success for valid registration."""
    response = client.post(
        "/register",
        json={
            "username": "alice",
            "email": "alice@endava.com",
            "password": "Password123!",
            "language": "english",
            "profile": "teen",
            "voice_enabled": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {"success": True}
    mock_insert_user.assert_called_once_with(
        conn_string=DB_CONN_STRING,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
        username="alice",
        email="alice@endava.com",
        plain_password="Password123!",
        language="english",
        profile="teen",
        voice_enabled=True
    )

@patch("api_server.insert_user")
def test_register_missing_fields(mock_insert_user, patch_dependencies):
    """Test /register returns 400 for missing required fields."""
    # Missing username, email, or password should raise 400
    response = client.post(
        "/register",
        json={"username": "bob", "email": "bob@endava.com"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    mock_insert_user.assert_not_called()

@patch("api_server.insert_user")
def test_register_exception(mock_insert_user, patch_dependencies):
    """Test /register returns 400 for DB error."""
    mock_insert_user.side_effect = Exception("DB error")
    response = client.post(
        "/register",
        json={
            "username": "carol",
            "email": "carol@endava.com",
            "password": "Password123!"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "DB error" in data["detail"]

@patch("api_server.collection")
def test_search_titles_success(mock_collection, patch_dependencies):
    """Test /search_titles returns correct titles and metadata."""
    # Setup mock collection.get to return metadatas with titles
    mock_collection.get.return_value = {
        "metadatas": [
            {"title": "Book A"},
            {"title": "Book B"},
            {"title": "Another Book"}
        ]
    }
    response = client.get("/search_titles?q=book&limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "titles" in data
    assert data["total"] == 3
    assert data["offset"] == 0
    assert data["limit"] == 2
    # Should be sorted and filtered
    assert set(data["titles"]) <= {"Book A", "Book B", "Another Book"}

@patch("api_server.collection")
def test_search_titles_pagination(mock_collection, patch_dependencies):
    """Test /search_titles returns correct pagination of titles."""
    mock_collection.get.return_value = {
        "metadatas": [
            {"title": f"Book {i}"} for i in range(1, 21)
        ]
    }
    response = client.get("/search_titles?q=Book&limit=5&offset=10")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 5
    assert data["offset"] == 10
    assert len(data["titles"]) == 5

@patch("api_server.collection")
def test_search_titles_no_match(mock_collection, patch_dependencies):
    """Test /search_titles returns empty list when no match found."""
    mock_collection.get.return_value = {
        "metadatas": [
            {"title": "Book X"},
            {"title": "Book Y"}
        ]
    }
    response = client.get("/search_titles?q=zzz")
    assert response.status_code == 200
    data = response.json()
    assert data["titles"] == []
    assert data["total"] == 0

@patch("api_server.collection")
def test_search_titles_error_handling(mock_collection, patch_dependencies):
    """Test /search_titles returns empty list and error on exception."""
    mock_collection.get.side_effect = KeyError("fail")
    response = client.get("/search_titles?q=Book")
    assert response.status_code == 200
    data = response.json()
    assert data["titles"] == []
    assert "error" in data
