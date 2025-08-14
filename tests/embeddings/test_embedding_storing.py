"""
Unit tests for embeddings.embedding_storing.
Covers:
- ChromaDB initialization and collection handling
- Loading book summaries from JSON
- Batch file discovery and sorting
- Embedding generation and storage logic (including resume and error handling)
- Main function batch processing, start/end indices, and exception handling
- Dummy response mocks for OpenAI embedding API
"""
from unittest.mock import patch, MagicMock
import json
import openai
import pytest
import embeddings.embedding_storing as es

def test_init_chroma():
    """Test that init_chroma returns the correct ChromaDB collection object."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    with patch("chromadb.PersistentClient", return_value=mock_client):
        result = es.init_chroma()
        assert result is mock_collection
        mock_client.get_or_create_collection.assert_called_once_with(es.COLLECTION_NAME)

def test_load_summaries(tmp_path):
    """Test that load_summaries loads book summaries and metadata from a JSON file."""
    data = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
    file = tmp_path / "summaries.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    result = es.load_summaries(str(file))
    assert result == data

def test_get_all_batch_files(monkeypatch):
    """Test that get_all_batch_files returns a sorted list of batch files."""
    files = ["b2.json", "b1.json", "b3.json"]
    monkeypatch.setattr(es.glob, "glob", lambda pattern: files)
    result = es.get_all_batch_files("irrelevant")
    assert result == sorted(files)

def test_embed_and_store_in_batches(monkeypatch):
    """Test embed_and_store_in_batches processes batches and calls collection.add for each book."""
    # Setup
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
    collection = MagicMock()
    collection.get.return_value = {"ids": []}
    # Patch openai.embeddings.create
    class DummyResp:
        """Mock response object for openai.embeddings.create, simulates embedding data."""
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr("embeddings.embedding_storing.openai.embeddings.create", lambda **kwargs:
        DummyResp([1.0, 2.0, 3.0]))
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=False)
    # Should call collection.add twice (once per book)
    assert collection.add.call_count == 2

def test_embed_and_store_in_batches_resume(monkeypatch):
    """Test embed_and_store_in_batches skips already inserted books when resume=True."""
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
    collection = MagicMock()
    collection.get.return_value = {"ids": ["Book1"]}
    class DummyResp:
        """Mock response object for openai.embeddings.create, simulates embedding data."""
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr("embeddings.embedding_storing.openai.embeddings.create", lambda **kwargs:
        DummyResp([1.0, 2.0, 3.0]))
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=True)
    # Only Book2 should be added
    assert collection.add.call_count == 1
    args, kwargs = collection.add.call_args
    assert "Book2" in kwargs["ids"]  # ids


def test_embed_and_store_in_batches_invalid_model(monkeypatch):
    """Test embed_and_store_in_batches raises ValueError for invalid embedding model."""
    collection = MagicMock()
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"}
    ]
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    # Patch openai.embeddings.create to avoid real API call
    class DummyResp:
        """Mock response object for openai.embeddings.create, simulates embedding data."""
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr(openai.embeddings, "create", lambda **kwargs:
        DummyResp([1.0, 2.0, 3.0]))
    with pytest.raises(ValueError):
        es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=False,
                                      embedding_model="not-a-real-model")

def test_main_full(monkeypatch):
    """Test main processes all batch files and prints correct total_books."""
    # Simulate 3 batch files, each with 2 books
    batch_files = ["batch1.json", "batch2.json", "batch3.json"]
    monkeypatch.setattr(es, "get_all_batch_files", lambda d: batch_files)
    monkeypatch.setattr(es, "load_openai_key", lambda: None)
    collection = MagicMock()
    monkeypatch.setattr(es, "init_chroma", lambda: collection)
    monkeypatch.setattr(es, "embed_and_store_in_batches", lambda c, s, **kwargs: None)
    monkeypatch.setattr(es, "load_summaries", lambda path: [{"title": f"Book-{path}-A"},
                                                            {"title": f"Book-{path}-B"}])
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0] if a else ""))
    es.main()
    # Should process all 3 batches
    assert any("Processing batch1.json..." in str(p) for p in printed)
    assert any("Processing batch2.json..." in str(p) for p in printed)
    assert any("Processing batch3.json..." in str(p) for p in printed)
    # Should print total_books = 6
    assert any("Finished inserting 6 books" in str(p) for p in printed)

def test_main_start_end(monkeypatch):
    """Test main processes only the specified start to end batch files."""
    batch_files = ["batch1.json", "batch2.json", "batch3.json", "batch4.json"]
    monkeypatch.setattr(es, "get_all_batch_files", lambda d: batch_files)
    monkeypatch.setattr(es, "load_openai_key", lambda: None)
    collection = MagicMock()
    monkeypatch.setattr(es, "init_chroma", lambda: collection)
    monkeypatch.setattr(es, "embed_and_store_in_batches", lambda c, s, **kwargs: None)
    monkeypatch.setattr(es, "load_summaries", lambda path: [{"title": f"Book-{path}-A"}])
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0] if a else ""))
    es.main(start=1, end=3)
    # Should process batch2.json and batch3.json only
    assert any("Processing batch2.json..." in str(p) for p in printed)
    assert any("Processing batch3.json..." in str(p) for p in printed)
    assert not any("Processing batch1.json..." in str(p) for p in printed)
    assert not any("Processing batch4.json..." in str(p) for p in printed)
    # Should print total_books = 2
    assert any("Finished inserting 2 books" in str(p) for p in printed)

def test_main_no_batches(monkeypatch):
    """Test main prints total_books=0 when no batch files are present."""
    monkeypatch.setattr(es, "get_all_batch_files", lambda d: [])
    monkeypatch.setattr(es, "load_openai_key", lambda: None)
    monkeypatch.setattr(es, "init_chroma", lambda: MagicMock())
    monkeypatch.setattr(es, "embed_and_store_in_batches", lambda c, s, **kwargs: None)
    monkeypatch.setattr(es, "load_summaries", lambda path: [])
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0] if a else ""))
    es.main()
    # Should print total_books = 0
    assert any("Finished inserting 0 books" in str(p) for p in printed)

def test_main_handles_exceptions(monkeypatch):
    """
    Test main prints batch processing and raises exception if embed_and_store_in_batches fails.
    """
    batch_files = ["batch1.json"]
    monkeypatch.setattr(es, "get_all_batch_files", lambda d: batch_files)
    monkeypatch.setattr(es, "load_openai_key", lambda: None)
    monkeypatch.setattr(es, "init_chroma", lambda: MagicMock())
    monkeypatch.setattr(es, "load_summaries", lambda path: [{"title": "Book1"}])
    def raise_exc(*a, **k):
        raise Exception("fail")
    monkeypatch.setattr(es, "embed_and_store_in_batches", raise_exc)
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0] if a else ""))
    try:
        es.main()
    except Exception as e:
        assert str(e) == "fail"
    # Should still print "Processing batch1.json..."
    assert any("Processing batch1.json..." in str(p) for p in printed)
