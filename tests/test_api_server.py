import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api_server import app

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

def test_recommend_returns_book_with_summary_and_image_url(patch_dependencies):
    patch_dependencies["search_books"].return_value = {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Book 1", "image_url": "http://img.com/1.png"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "A summary."
    response = client.post("/recommend", json={"query": "adventure"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Book 1"
    assert data["summary"] == "A summary."
    assert data["image_url"] == "http://img.com/1.png"

def test_recommend_generates_image_if_missing(patch_dependencies):
    patch_dependencies["search_books"].return_value = {
        "ids": [["id2"]],
        "metadatas": [[{"title": "Book 2"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "Another summary."
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/2.png"
    response = client.post("/recommend", json={"query": "mystery"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Book 2"
    assert data["summary"] == "Another summary."
    assert data["image_url"] == "http://img.com/2.png"
    patch_dependencies["collection"].update.assert_called_once()

def test_recommend_skips_books_without_summary(patch_dependencies):
    patch_dependencies["search_books"].return_value = {
        "ids": [["id3", "id4"]],
        "metadatas": [[{"title": "Book 3"}, {"title": "Book 4"}]]
    }
    # First book: no summary, second book: has summary
    patch_dependencies["get_summary_by_title"].side_effect = ["Summary not found.", "Good summary."]
    patch_dependencies["generate_image_from_summary"].return_value = "http://img.com/4.png"
    response = client.post("/recommend", json={"query": "fantasy"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Book 4"
    assert data["summary"] == "Good summary."
    assert data["image_url"] == "http://img.com/4.png"

def test_recommend_returns_error_if_no_suitable_book(patch_dependencies):
    patch_dependencies["search_books"].return_value = {
        "ids": [["id5"]],
        "metadatas": [[{"title": "Book 5"}]]
    }
    patch_dependencies["get_summary_by_title"].return_value = "Summary not found."
    response = client.post("/recommend", json={"query": "unknown"})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

def test_voice_returns_transcribed_text(patch_dependencies):
    patch_dependencies["listen_with_whisper"].return_value = "hello world"
    response = client.post("/voice", json={"language": "english"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "hello world"

def test_voice_uses_correct_language_code(patch_dependencies):
    patch_dependencies["listen_with_whisper"].return_value = "salut lume"
    response = client.post("/voice", json={"language": "romanian"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "salut lume"