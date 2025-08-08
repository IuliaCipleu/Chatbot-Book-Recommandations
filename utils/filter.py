"""
This module provides utilities for filtering offensive content from text using a configurable list
of bad words.
"""
import json

def load_bad_words(json_path="data/bad_words.json"):
    """
    Loads a list of bad words from a JSON file and returns them as a set.

    Args:
        json_path (str, optional): Path to the JSON file containing bad words.
        Defaults to "data/bad_words.json".

    Returns:
        set: A set of bad words loaded from the file. Returns an empty set if loading fails.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load bad words list: {e}")
        return set()

BAD_WORDS = load_bad_words()

def is_offensive(text):
    """
    Checks if the given text contains any offensive words from the BAD_WORDS set.

    Args:
        text (str): The text to check for offensive content.

    Returns:
        bool: True if any bad word is found in the text, False otherwise.
    """
    return any(word in text.lower().split() for word in BAD_WORDS)
