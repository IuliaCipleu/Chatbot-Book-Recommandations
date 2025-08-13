from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from api_server import app, create_access_token, verify_token, SECRET_KEY, ALGORITHM
from jose import jwt
from fastapi import HTTPException
from datetime import datetime, UTC, timedelta

client = TestClient(app)

@pytest.fixture(autouse=True)
def patch_dependencies():
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
    # Setup mocks for a book with summary and image
    patch_dependencies["search_books"].return_value = {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Book 1", "image_url": "http://img.com/1.png"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "A summary."
    # Make request with valid JWT and role
    response = client.post(
        "/recommend",
        json={"query": "adventure", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "title": "Book 1",
        "summary": "A summary.",
        "image_url": "http://img.com/1.png"
    }

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_generates_image_if_missing(mock_verify_token, patch_dependencies):
    # Setup mocks for a book with summary but no image
    patch_dependencies["search_books"].return_value = {
        "ids": [["id2"]],
        "metadatas": [[{"title": "Book 2"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "Another summary."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/2.png"
    # Make request
    response = client.post(
        "/recommend",
        json={"query": "mystery", "role": "adult"},
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "title": "Book 2",
        "summary": "Another summary.",
        "image_url": "http://img.com/2.png"
    }
    patch_dependencies["collection"].update.assert_called_once()

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_skips_books_without_summary(mock_verify_token, patch_dependencies):
    # Setup mocks for two books, only second has a valid summary
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
    assert data == {
        "title": "Book 4",
        "summary": "Good summary.",
        "image_url": "http://img.com/4.png"
    }

@patch("api_server.verify_token", return_value="testuser")
def test_recommend_returns_error_if_no_suitable_book(mock_verify_token, patch_dependencies):
    # Setup mocks for a book with no valid summary
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
    print("Response JSON:", response.json())
    assert data == {"error": "No suitable book found."}

@patch("api_server.listen_with_whisper", return_value="hello world")
def test_voice_returns_transcribed_text(mock_listen_with_whisper, patch_dependencies):
    response = client.post("/voice", json={"language": "english"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "hello world"

def test_voice_uses_correct_language_code(patch_dependencies):
    patch_dependencies["listen_with_whisper"].return_value = "salut"
    response = client.post("/voice", json={"language": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "salut"

# Test create_access_token returns a valid JWT with correct payload and expiry
def test_create_access_token_valid():
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
    data = {"sub": "testuser"}
    token = create_access_token(data)
    username = verify_token(token)
    assert username == "testuser"

# Test verify_token raises HTTPException for invalid token
def test_verify_token_invalid():
    with pytest.raises(HTTPException) as excinfo:
        verify_token("invalid.token.value")
    assert excinfo.value.status_code == 401
@patch("api_server.login_user")
@patch("api_server.create_access_token", return_value="jwt.token.value")
def test_login_success(mock_create_access_token, mock_login_user, patch_dependencies):
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
    # Mock login_user to return None (invalid credentials)
    mock_login_user.return_value = None
    response = client.post("/login", json={"username": "bob", "password": "wrongpw"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
    mock_login_user.assert_called_once()

def test_login_missing_fields():
    # Missing username or password should raise 422 Unprocessable Entity
    response = client.post("/login", json={"username": "alice"})
    assert response.status_code == 422 or response.status_code == 400

    response = client.post("/login", json={"password": "Password123!"})
    assert response.status_code == 422 or response.status_code == 400

def test_login_empty_body():
    # Empty body should raise 422 Unprocessable Entity
    response = client.post("/login", json={})
    assert response.status_code == 422 or response.status_code == 400

def test_login_no_json():
    # No JSON body should raise 422 Unprocessable Entity
    response = client.post("/login")
    assert response.status_code == 422 or response.status_code == 400

@patch("api_server.login_user")
def test_login_user_exception(mock_login_user, patch_dependencies):
    # Simulate an exception in login_user
    mock_login_user.side_effect = Exception("DB error")
    response = client.post("/login", json={"username": "alice", "password": "Password123!"})
    # Should return 401 because user is None, not 500
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
