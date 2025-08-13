from unittest.mock import patch, MagicMock
import embeddings.embedding_storing as es
import json
import openai
import pytest

def test_init_chroma():
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    with patch("chromadb.PersistentClient", return_value=mock_client):
        result = es.init_chroma()
        assert result is mock_collection
        mock_client.get_or_create_collection.assert_called_once_with(es.COLLECTION_NAME)

def test_load_summaries(tmp_path):
    data = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
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
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
    collection = MagicMock()
    collection.get.return_value = {"ids": []}
    # Patch openai.embeddings.create
    class DummyResp:
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
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"},
        {"title": "Book2", "summary": "Summary2", "genre": ["Nonfiction"], "author": "Author2"}
    ]
    collection = MagicMock()
    collection.get.return_value = {"ids": ["Book1"]}
    class DummyResp:
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
    collection = MagicMock()
    summaries = [
        {"title": "Book1", "summary": "Summary1", "genre": ["Fiction"], "author": "Author1"}
    ]
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    # Patch openai.embeddings.create to avoid real API call
    class DummyResp:
        def __init__(self, emb):
            self.data = [MagicMock(embedding=emb)]
    monkeypatch.setattr(openai.embeddings, "create", lambda **kwargs:
        DummyResp([1.0, 2.0, 3.0]))
    with pytest.raises(ValueError):
        es.embed_and_store_in_batches(collection, summaries, batch_size=1, resume=False, embedding_model="not-a-real-model")

def test_main_full(monkeypatch):
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
    batch_files = ["batch1.json"]
    monkeypatch.setattr(es, "get_all_batch_files", lambda d: batch_files)
    monkeypatch.setattr(es, "load_openai_key", lambda: None)
    monkeypatch.setattr(es, "init_chroma", lambda: MagicMock())
    monkeypatch.setattr(es, "load_summaries", lambda path: [{"title": "Book1"}])
    def raise_exc(*a, **k): raise Exception("fail")
    monkeypatch.setattr(es, "embed_and_store_in_batches", raise_exc)
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0] if a else ""))
    try:
        es.main()
    except Exception as e:
        assert str(e) == "fail"
    # Should still print "Processing batch1.json..."
    assert any("Processing batch1.json..." in str(p) for p in printed)
