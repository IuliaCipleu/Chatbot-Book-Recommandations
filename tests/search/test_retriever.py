"""
Unit tests for the retriever logic in the search module.
Covers retrieval, ranking, and validation of book search results.
Mocks external dependencies for isolated testing.
"""
from unittest.mock import patch, MagicMock
import pytest
from pytest import fixture
from search.retriever import search_books

@pytest.fixture
def mock_collection_fixture():
    """
    Pytest fixture that returns a MagicMock for the collection object.
    Used to mock database interactions in tests.
    """
    # setup code
    return MagicMock()

@fixture
def mock_collection():
    """
    Pytest fixture that returns a MagicMock with a preset query return value.
    Used to mock collection queries in tests.
    """
    mock = MagicMock()
    mock.query.return_value = {"documents": ["book1", "book2"], "ids": [1, 2]}
    return mock

@patch("search.retriever.openai")
@patch("search.retriever.load_openai_key")
def test_search_books_success(_, mock_openai, mock_collection_fixture):
    """
    Test that search_books returns expected documents and calls OpenAI embedding and collection
    query.
    """
    # Mock embedding response
    mock_embedding = MagicMock()
    mock_embedding.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_openai.api_key = "test-key"
    mock_openai.embeddings.create.return_value = mock_embedding
    # Set expected query return value
    mock_collection_fixture.query.return_value = {"documents": ["book1", "book2"], "ids": [1, 2]}

    result = search_books("test query", mock_collection_fixture, top_k=2, model="test-model")
    assert "documents" in result
    assert result["documents"] == ["book1", "book2"]
    mock_collection_fixture.query.assert_called_once_with(query_embeddings=[[0.1, 0.2, 0.3]],
                                                          n_results=2)
    mock_openai.embeddings.create.assert_called_once_with(input="test query", model="test-model")

@patch("search.retriever.openai")
@patch("search.retriever.load_openai_key")
def test_search_books_loads_api_key_if_missing(mock_load_key, mock_openai, mock_collection,
                                               mock_collection_fixture):
    """
    Test that search_books loads the OpenAI API key if it is missing and proceeds with search.
    """
    # Simulate missing API key initially, then set after loading
    mock_openai.api_key = None
    def set_key():
        mock_openai.api_key = "loaded-key"
    mock_load_key.side_effect = set_key

    mock_embedding = MagicMock()
    mock_embedding.data = [MagicMock(embedding=[0.4, 0.5])]
    mock_openai.embeddings.create.return_value = mock_embedding
    # Set expected query return value
    mock_collection_fixture.query.return_value = {"documents": ["book1", "book2"], "ids": [1, 2]}

    result = search_books("another query", mock_collection_fixture)
    assert "documents" in result
    mock_load_key.assert_called_once()

@patch("search.retriever.openai")
@patch("search.retriever.load_openai_key")
def test_search_books_raises_if_api_key_not_set(mock_load_key, mock_openai, mock_collection,
                                                mock_collection_fixture):
    """
    Test that search_books raises ValueError if OpenAI API key is not set after attempting to load.
    """
    mock_openai.api_key = None
    mock_load_key.return_value = None  # API key still not set

    with pytest.raises(ValueError, match="OpenAI API key is not set."):
        search_books("fail query", mock_collection_fixture)
