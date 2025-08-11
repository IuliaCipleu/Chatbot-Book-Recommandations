import pytest
from unittest.mock import patch, mock_open
import json

from utils import filter as filter_mod

def test_load_bad_words_valid():
    data = json.dumps(["badword1", "badword2"])
    with patch("builtins.open", mock_open(read_data=data)):
        result = filter_mod.load_bad_words("dummy.json")
        assert result == {"badword1", "badword2"}

def test_load_bad_words_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = filter_mod.load_bad_words("missing.json")
        assert result == set()

def test_load_bad_words_invalid_json():
    with patch("builtins.open", mock_open(read_data="not json")):
        result = filter_mod.load_bad_words("bad.json")
        assert result == set()

def test_is_offensive_true():
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert filter_mod.is_offensive("This is a badword in text.")

def test_is_offensive_false():
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert not filter_mod.is_offensive("This is clean text.")

def test_is_offensive_case_insensitive():
    with patch.object(filter_mod, "BAD_WORDS", {"badword"}):
        assert filter_mod.is_offensive("BADWORD appears here.")

def test_is_offensive_word_boundary():
    with patch.object(filter_mod, "BAD_WORDS", {"bad"}):
        # Should not match 'badly' as 'bad' (split by space)
        assert not filter_mod.is_offensive("He behaved badly.")
        assert filter_mod.is_offensive("He is bad.")
