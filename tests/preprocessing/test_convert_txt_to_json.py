"""
Unit tests for preprocessing.convert_txt_to_json.parse_cmu_book_summary.
Covers:
- Basic parsing of book summaries with multiple genres and books.
- Limiting the number of parsed books using max_books.
- Skipping incomplete lines in the input file.
- Handling empty input files.
- Ensuring only one book per genre is included in the output.
"""
import os
import tempfile
import json
from preprocessing.convert_txt_to_json import parse_cmu_book_summary

def make_sample_txt(content):
    """Create a temporary text file with the given content and return its path."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def read_json(path):
    """Read and return JSON data from the specified file path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_parse_cmu_book_summary_basic(tmp_path):
    """Test parsing a basic book summary file with two books and two genres."""
    # 2 genres, 2 books, each covers a genre
    txt = (
        "1\t/fb1\tBook1\tAuthor1\t2000\tFantasy,Adventure\tSummary1\n"
        "2\t/fb2\tBook2\tAuthor2\t2001\tMystery\tSummary2\n"
    )
    txt_path = make_sample_txt(txt)
    json_path = tmp_path / "out.json"
    parse_cmu_book_summary(txt_path, str(json_path), max_books=10)
    data = read_json(json_path)
    assert "Book1" in data or "Book2" in data
    assert len(data) == 2
    os.remove(txt_path)

def test_parse_cmu_book_summary_max_books(tmp_path):
    """Test that max_books parameter limits the number of books parsed."""
    txt = (
        "1\t/fb1\tBook1\tAuthor1\t2000\tFantasy\tSummary1\n"
        "2\t/fb2\tBook2\tAuthor2\t2001\tMystery\tSummary2\n"
        "3\t/fb3\tBook3\tAuthor3\t2002\tAdventure\tSummary3\n"
    )
    txt_path = make_sample_txt(txt)
    json_path = tmp_path / "out.json"
    parse_cmu_book_summary(txt_path, str(json_path), max_books=2)
    data = read_json(json_path)
    assert len(data) == 2
    os.remove(txt_path)

def test_parse_cmu_book_summary_skips_incomplete_lines(tmp_path):
    """Test that incomplete lines in the input file are skipped during parsing."""
    txt = (
        "1\t/fb1\tBook1\tAuthor1\t2000\tFantasy\tSummary1\n"
        "2\t/fb2\tBook2\tAuthor2\t2001\tMystery\n"  # incomplete
        "3\t/fb3\tBook3\tAuthor3\t2002\tAdventure\tSummary3\n"
    )
    txt_path = make_sample_txt(txt)
    json_path = tmp_path / "out.json"
    parse_cmu_book_summary(txt_path, str(json_path), max_books=10)
    data = read_json(json_path)
    assert "Book2" not in data
    assert "Book1" in data and "Book3" in data
    os.remove(txt_path)

def test_parse_cmu_book_summary_empty_file(tmp_path):
    """Test parsing an empty file results in an empty dictionary."""
    txt_path = make_sample_txt("")
    json_path = tmp_path / "out.json"
    parse_cmu_book_summary(txt_path, str(json_path), max_books=10)
    data = read_json(json_path)
    assert data == {}
    os.remove(txt_path)

def test_parse_cmu_book_summary_duplicate_genre(tmp_path):
    """Test that only one book per genre is included in the output."""
    txt = (
        "1\t/fb1\tBook1\tAuthor1\t2000\tFantasy\tSummary1\n"
        "2\t/fb2\tBook2\tAuthor2\t2001\tFantasy\tSummary2\n"
    )
    txt_path = make_sample_txt(txt)
    json_path = tmp_path / "out.json"
    parse_cmu_book_summary(txt_path, str(json_path), max_books=10)
    data = read_json(json_path)
    # Only one book per genre should be included
    assert len(data) == 1
    os.remove(txt_path)
