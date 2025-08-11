import pytest
import json
import os
from unittest.mock import patch, mock_open
from search.summary_tool import get_summary_by_title

def test_summary_found_in_first_batch(monkeypatch):
    # Mock glob to return two files
    batch_files = ["batch1.json", "batch2.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    # Mock open to return a summary in the first file
    summaries1 = {"Book A": "Summary A"}
    summaries2 = {"Book B": "Summary B"}
    m = mock_open(read_data=json.dumps(summaries1))
    m2 = mock_open(read_data=json.dumps(summaries2))
    open_map = {"batch1.json": m.return_value, "batch2.json": m2.return_value}
    def open_side_effect(file, *args, **kwargs):
        return open_map[file]
    with patch("builtins.open", side_effect=open_side_effect):
        result = get_summary_by_title("Book A", batches_dir="unused")
        assert result == "Summary A"

def test_summary_found_in_second_batch(monkeypatch):
    batch_files = ["batch1.json", "batch2.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    summaries1 = {"Book X": "Summary X"}
    summaries2 = {"Book Y": "Summary Y"}
    m = mock_open(read_data=json.dumps(summaries1))
    m2 = mock_open(read_data=json.dumps(summaries2))
    open_map = {"batch1.json": m.return_value, "batch2.json": m2.return_value}
    def open_side_effect(file, *args, **kwargs):
        return open_map[file]
    with patch("builtins.open", side_effect=open_side_effect):
        result = get_summary_by_title("Book Y", batches_dir="unused")
        assert result == "Summary Y"

def test_summary_not_found(monkeypatch):
    batch_files = ["batch1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    summaries1 = {"Book X": "Summary X"}
    m = mock_open(read_data=json.dumps(summaries1))
    with patch("builtins.open", m):
        result = get_summary_by_title("Book Z", batches_dir="unused")
        assert result == "Summary not found."

def test_no_batch_files(monkeypatch):
    monkeypatch.setattr("glob.glob", lambda pattern: [])
    result = get_summary_by_title("Any Book", batches_dir="unused")
    assert result == "Summary not found."

def test_empty_batch_file(monkeypatch):
    batch_files = ["batch1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    m = mock_open(read_data="{}")
    with patch("builtins.open", m):
        result = get_summary_by_title("Book Z", batches_dir="unused")
        assert result == "Summary not found."

def test_malformed_json(monkeypatch):
    batch_files = ["batch1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    m = mock_open(read_data="{not a json}")
    with patch("builtins.open", m):
        # Should raise json.JSONDecodeError
        with pytest.raises(json.JSONDecodeError):
            get_summary_by_title("Book Z", batches_dir="unused")

def test_summary_found(monkeypatch):
    # Simulate one batch file containing the book
    batch_files = ["data/batches/book_summaries_batch_1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    summaries = {"Book Title": "This is the summary."}
    m = mock_open(read_data=json.dumps(summaries))
    with patch("builtins.open", m):
        result = get_summary_by_title("Book Title", batches_dir="data/batches")
        assert result == "This is the summary."

def test_summary_not_found(monkeypatch):
    # Simulate one batch file without the book
    batch_files = ["data/batches/book_summaries_batch_1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    summaries = {"Other Book": "Other summary."}
    m = mock_open(read_data=json.dumps(summaries))
    with patch("builtins.open", m):
        result = get_summary_by_title("Missing Book", batches_dir="data/batches")
        assert result == "Summary not found."

def test_multiple_batches(monkeypatch):
    # Simulate two batch files, book in the second
    batch_files = [
        "data/batches/book_summaries_batch_1.json",
        "data/batches/book_summaries_batch_2.json"
    ]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    summaries1 = {"Book A": "Summary A"}
    summaries2 = {"Book B": "Summary B"}
    m1 = mock_open(read_data=json.dumps(summaries1))
    m2 = mock_open(read_data=json.dumps(summaries2))
    open_map = {
        batch_files[0]: m1.return_value,
        batch_files[1]: m2.return_value
    }
    def open_side_effect(file, *args, **kwargs):
        return open_map[file]
    with patch("builtins.open", side_effect=open_side_effect):
        result = get_summary_by_title("Book B", batches_dir="data/batches")
        assert result == "Summary B"

def test_no_batch_files(monkeypatch):
    # Simulate no batch files present
    monkeypatch.setattr("glob.glob", lambda pattern: [])
    result = get_summary_by_title("Any Book", batches_dir="data/batches")
    assert result == "Summary not found."

def test_empty_batch_file(monkeypatch):
    # Simulate empty JSON file
    batch_files = ["data/batches/book_summaries_batch_1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    m = mock_open(read_data="{}")
    with patch("builtins.open", m):
        result = get_summary_by_title("Book Z", batches_dir="data/batches")
        assert result == "Summary not found."

def test_malformed_json_batches(monkeypatch):
    # Simulate malformed JSON file
    batch_files = ["data/batches/book_summaries_batch_1.json"]
    monkeypatch.setattr("glob.glob", lambda pattern: batch_files)
    m = mock_open(read_data="{not a json}")
    with patch("builtins.open", m):
        with pytest.raises(json.JSONDecodeError):
            get_summary_by_title("Book Z", batches_dir="data/batches")
