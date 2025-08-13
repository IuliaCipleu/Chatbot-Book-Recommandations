"""
Unit tests for the 'filter' utility module.
This test suite covers:
- Loading bad words from a JSON file, including valid, missing, and invalid files.
- Checking if a text contains offensive words, with tests for case insensitivity and
word boundaries.
Mocks are used to simulate file I/O and module state.
"""
from unittest.mock import patch, mock_open
import json

from utils import filter as filter_mod

def test_load_bad_words_valid():
    """
    Test that load_bad_words loads a valid JSON file and returns a set of bad words.
    """
    data = json.dumps(["badword1", "badword2"])
    with patch("builtins.open", mock_open(read_data=data)):
        result = filter_mod.load_bad_words("dummy.json")
        assert result == {"badword1", "badword2"}

def test_load_bad_words_file_not_found():
    """
    Test that load_bad_words returns an empty set when the file is not found.
    """
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = filter_mod.load_bad_words("missing.json")
        assert result == set()

def test_load_bad_words_invalid_json():
    """
    Test that load_bad_words returns an empty set when the file contains invalid JSON.
    """
    with patch("builtins.open", mock_open(read_data="not json")):
        result = filter_mod.load_bad_words("bad.json")
        assert result == set()

def test_is_offensive_true():
    """
    Test that is_offensive returns True when the text contains a bad word.
    """
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert filter_mod.is_offensive("This is a badword in text.")

def test_is_offensive_false():
    """
    Test that is_offensive returns False when the text does not contain any bad words.
    """
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert not filter_mod.is_offensive("This is clean text.")

def test_is_offensive_case_insensitive():
    """
    Test that is_offensive is case-insensitive when matching bad words.
    """
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert filter_mod.is_offensive("BADWORD appears here.")

def test_is_offensive_word_boundary():
    """
    Test that is_offensive matches bad words only as whole words, not substrings.
    """
    with patch.object(filter_mod, "BAD_WORDS", {"bad"}):
        # Should not match 'badly' as 'bad' (split by space)
        assert not filter_mod.is_offensive("He behaved badly.")
        assert filter_mod.is_offensive("He is bad.")
