"""
Unit tests for the `load_openai_key` function in `utils.openai_config`.
Tests:
- Setting the OpenAI API key from the environment variable.
- Stripping leading/trailing whitespace from the API key.
- Raising a ValueError when the environment variable is missing.
"""
import os
from unittest import mock
import pytest
from utils.openai_config import load_openai_key

def test_load_openai_key_sets_api_key(monkeypatch):
    """Test that the OpenAI API key is set when the environment variable is present."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    with mock.patch("openai.api_key", new_callable=mock.PropertyMock) as _:
        load_openai_key()
        assert os.getenv("OPENAI_API_KEY") == "test-key-123"

def test_load_openai_key_strips_whitespace(monkeypatch):
    """Test that leading/trailing whitespace is stripped from the API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "  test-key-456  ")
    with mock.patch("openai.api_key", new_callable=mock.PropertyMock) as _:
        load_openai_key()
        assert os.getenv("OPENAI_API_KEY").strip() == "test-key-456"

def test_load_openai_key_raises_when_missing(monkeypatch):
    """Test that ValueError is raised if the environment variable is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY not set in environment."):
        load_openai_key()
