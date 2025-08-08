"""
This module provides a utility function to retrieve a book summary by title from a JSON file.
"""
import json

def get_summary_by_title(title, json_path="data/book_summaries.json"):
    """
    Retrieves the summary of a book by its title from a JSON file.

    Args:
        title (str): The title of the book.
        json_path (str, optional): Path to the JSON file containing book summaries.
                                   Defaults to "data/book_summaries.json".

    Returns:
        str: The summary of the book if found, otherwise "Summary not found."
    """
    with open(json_path, "r", encoding="utf-8") as f:
        summaries = json.load(f)
    return summaries.get(title, "Summary not found.")
