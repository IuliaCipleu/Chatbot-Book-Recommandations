import pytest
from unittest.mock import patch, MagicMock
import embeddings.embedding_storing as es
import json

def test_init_chroma():
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    with patch("chromadb.PersistentClient", return_value=mock_client):
        result = es.init_chroma()
        assert result is mock_collection
        mock_client.get_or_create_collection.assert_called_once_with(es.COLLECTION_NAME)

def test_load_summaries(tmp_path):
    data = {"Book1": "Summary1", "Book2": "Summary2"}
    file = tmp_path / "summaries.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    result = es.load_summaries(str(file))
    assert result == data

def test_get_all_batch_files(monkeypatch):
    files = ["b2.json", "b1.json", "b3.json"]
    monkeypatch.setattr(es.glob, "glob", lambda pattern: files)
    result = es.get_all_batch_files("irrelevant")
    assert result == sorted(files)

def test_embed_and_store_in_batches(monkeypatch):
    # Setup
    summaries = {"Book1": "Summary1", "Book2": "Summary2"}
    collection = MagicMock()
    collection.get.return_value = {"ids": []}
    # Patch openai.embeddings.create
    class DummyResp:
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr(es.openai.embeddings, "create", lambda **kwargs: DummyResp([1.0, 2.0, 3.0]))
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=False)
    # Should call collection.add twice (once per book)
    assert collection.add.call_count == 2

def test_embed_and_store_in_batches_resume(monkeypatch):
    summaries = {"Book1": "Summary1", "Book2": "Summary2"}
    collection = MagicMock()
    collection.get.return_value = {"ids": ["Book1"]}
    class DummyResp:
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr(es.openai.embeddings, "create", lambda **kwargs: DummyResp([1.0, 2.0, 3.0]))
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=True)
    # Only Book2 should be added
    assert collection.add.call_count == 1
    args, kwargs = collection.add.call_args
    assert "Book2" in kwargs["ids"]  # ids


def test_embed_and_store_in_batches_invalid_model(monkeypatch):
    collection = MagicMock()
    summaries = {"Book1": "Summary1"}
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    # Patch openai.embeddings.create to avoid real API call
    class DummyResp:
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr(es.openai.embeddings, "create", lambda **kwargs: DummyResp([1.0, 2.0, 3.0]))
    with pytest.raises(ValueError):
        es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=False, embedding_model="not-a-real-model")
