"""
This module provides a utility function to retrieve a book summary by title from a JSON file.
"""
import json
import os
import glob

def get_summary_by_title(title, batches_dir="data/batches"):
    """
    Retrieves the summary of a book by its title from all JSON batch files in a folder.

    Args:
        title (str): The title of the book.
        batches_dir (str, optional): Directory containing JSON batch files.
        Defaults to "data/batches".

    Returns:
        str: The summary of the book if found, otherwise "Summary not found."
    """
    json_files = glob.glob(os.path.join(batches_dir, "book_summaries_*.json"))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            books = json.load(f)
            # books is a list of dicts with 'title' and 'summary'
            if isinstance(books, dict):
                # fallback for old format
                if title in books:
                    return books[title]
            elif isinstance(books, list):
                for book in books:
                    if book.get("title") == title:
                        return book.get("summary", "Summary not found.")
    return "Summary not found."
