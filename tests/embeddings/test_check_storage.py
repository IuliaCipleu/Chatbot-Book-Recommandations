import pytest
import chromadb
from embeddings import check_storage
import io
import sys
import io
import sys

class DummyCollection:
    def __init__(self, ids):
        self._ids = ids
    def get(self):
        return {"ids": self._ids}

class DummyClient:
    def __init__(self, ids):
        self._collection = DummyCollection(ids)
    def get_or_create_collection(self, name):
        return self._collection

def test_number_of_books_stored(monkeypatch):
    dummy_ids = ["id1", "id2", "id3"]
    dummy_client = DummyClient(dummy_ids)

    monkeypatch.setattr(check_storage, "chromadb", chromadb)
    monkeypatch.setattr(chromadb, "PersistentClient", lambda path: dummy_client)

    # Capture print output
    captured = io.StringIO()
    sys.stdout = captured

    # Run the script logic
    check_storage.client = dummy_client
    check_storage.collection = dummy_client.get_or_create_collection("books")
    result = check_storage.collection.get()
    print("Number of books stored:", len(result.get("ids", [])))

    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert "Number of books stored: 3" in output

def test_empty_collection(monkeypatch):
    dummy_ids = []
    dummy_client = DummyClient(dummy_ids)

    monkeypatch.setattr(check_storage, "chromadb", chromadb)
    monkeypatch.setattr(chromadb, "PersistentClient", lambda path: dummy_client)

    captured = io.StringIO()
    sys.stdout = captured

    check_storage.client = dummy_client
    check_storage.collection = dummy_client.get_or_create_collection("books")
    result = check_storage.collection.get()
    print("Number of books stored:", len(result.get("ids", [])))

    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert "Number of books stored: 0" in output