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
    batch_files = glob.glob(os.path.join(batches_dir, "book_summaries_batch_*.json"))
    for batch_file in batch_files:
        with open(batch_file, "r", encoding="utf-8") as f:
            summaries = json.load(f)
            if title in summaries:
                return summaries[title]
    return "Summary not found."
