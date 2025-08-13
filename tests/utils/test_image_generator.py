from unittest.mock import patch, MagicMock
from utils.image_generator import generate_image_from_summary

def test_generate_image_success():
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="http://fake-url.com/image.png")]
    with patch("openai.images.generate", return_value=mock_response) as mock_generate:
        url = generate_image_from_summary("Test Book", "A summary.")
        assert url == "http://fake-url.com/image.png"
        mock_generate.assert_called_once()
        _, kwargs = mock_generate.call_args
        assert kwargs["model"] == "dall-e-3"
        assert "Test Book" in kwargs["prompt"]
        assert "A summary." in kwargs["prompt"]

def test_generate_image_exception():
    with patch("openai.images.generate", side_effect=Exception("API error")):
        url = generate_image_from_summary("Test Book", "A summary.")
        assert url is None

def test_generate_image_empty_summary():
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="http://fake-url.com/empty.png")]
    with patch("openai.images.generate", return_value=mock_response):
        url = generate_image_from_summary("Empty Book", "")
        assert url == "http://fake-url.com/empty.png"

def test_generate_image_no_data_in_response(monkeypatch):
    class DummyResponse:
        data = []
    def fake_generate(*a, **k):
        return DummyResponse()
    monkeypatch.setattr("openai.images.generate", fake_generate)
    result = generate_image_from_summary("title", "summary")
    assert result is None

def test_generate_image_prompt_content():
    with patch("openai.images.generate") as mock_generate:
        generate_image_from_summary("Prompt Book", "Prompt summary.")
        prompt = mock_generate.call_args[1]["prompt"]
        assert "Prompt Book" in prompt
        assert "Prompt summary." in prompt
        assert "book cover" in prompt or "scene" in prompt
