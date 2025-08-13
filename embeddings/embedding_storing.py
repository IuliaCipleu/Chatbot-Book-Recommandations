"""
embedding_storing.py

Script for embedding book summaries using OpenAI and storing them in a ChromaDB collection.

Features:
- Loads book summaries and metadata from genre-based JSON files (list of dicts)
- Generates OpenAI embeddings for each summary (supports multiple embedding models)
- Stores embeddings, metadata (title, genre, author), and document text in ChromaDB
- Skips already-inserted books (resume mode) and avoids duplicates in each batch
- Supports partial processing via --start and --end batch indices
- Prints progress and batch statistics

Integrations:
- ChromaDB for vector storage and metadata
- OpenAI for embedding generation

Recommended to run after preprocessing with split_txt_to_json_batches.py
"""

import os
import sys
import glob
import json
import argparse
import openai
import chromadb
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.openai_config import load_openai_key

# Folder containing JSON batches
BATCHES_DIR = "data/batches"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "books"

def init_chroma():
    """
    Initializes and returns a ChromaDB collection for storing book embeddings.

    Returns:
        chromadb.api.models.Collection.Collection: The ChromaDB collection object.
    """
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    return chroma_client.get_or_create_collection(COLLECTION_NAME)


def load_summaries(path):
    """
    Loads book summaries and metadata from a JSON file (list of dicts).
    Args:
        path (str): Path to the JSON file containing book summaries.
    Returns:
        list: List of dicts with keys title, summary, genre, author.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_batch_files(batches_dir):
    """
    Returns a sorted list of all JSON batch files in the given directory.
    """
    return sorted(glob.glob(os.path.join(batches_dir, "book_summaries_*.json")))

def embed_and_store_in_batches(collection, summaries, batch_size=100, resume=True,
                               embedding_model="text-embedding-3-small"):
    """
    Generates embeddings for book summaries and stores them in ChromaDB in batches.
    Resumes from where it left off if resume=True.

    Args:
        collection (chromadb.api.models.Collection.Collection): The ChromaDB collection to
        store embeddings.
        summaries (dict): Dictionary mapping book titles to summaries.
        batch_size (int): Number of books to process per batch.
        resume (bool): If True, skip books already in the collection.
    """
    allowed_models = [
        "text-embedding-3-small",
        "text-embedding-4o-mini",
        "text-embedding-4.1-mini",
        "text-embedding-4.1-nano"
    ]
    if embedding_model not in allowed_models:
        raise ValueError(f"Embedding model '{embedding_model}' is not allowed.",
                         f"Allowed models: {allowed_models}")

    # Get already inserted IDs if resuming
    existing_ids = set()
    if resume:
        try:
            existing = collection.get()
            for id_ in existing.get("ids", []):
                existing_ids.add(id_)
        except (AttributeError, KeyError):
            pass

    total = len(summaries)
    i = 0
    while i < total:
        batch = []
        batch_titles = []
        batch_ids = []
        batch_metas = []
        seen_titles = set()
        for j in range(i, min(i+batch_size, total)):
            book = summaries[j]
            title = book.get("title")
            summary = book.get("summary")
            genre = book.get("genre")
            author = book.get("author")
            if not title or not summary:
                continue
            if resume and title in existing_ids:
                continue
            if title in seen_titles:
                continue  # skip duplicate in this batch
            seen_titles.add(title)
            input_text = f"{title}: {summary}"
            batch.append(input_text)
            batch_titles.append(title)
            batch_ids.append(title)
            genre_str = ", ".join(genre) if isinstance(genre, list) else (genre if genre else None)
            batch_metas.append({"title": title, "genre": genre_str, "author": author})
        if not batch:
            i += batch_size
            continue
        # Get embeddings for the batch
        embeddings = []
        for input_text in batch:
            response = openai.embeddings.create(
                input=input_text,
                model=embedding_model
            )
            embeddings.append(response.data[0].embedding)
        collection.add(
            documents=batch,
            embeddings=embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )
        print(f"Inserted batch {i//batch_size+1} ({len(batch)} books)")
        i += batch_size
    print("All batches processed.")

def main(start=0, end=None):
    """
    Main function to load API key, initialize ChromaDB, load summaries, and store embeddings.
    Can process only a subset of batch files using start and end indices.
    """
    load_openai_key()  # Check and set API key
    collection = init_chroma()
    batch_files = get_all_batch_files(BATCHES_DIR)
    if end is None:
        end = len(batch_files)
    total_books = 0
    for batch_file in batch_files[start:end]:
        print(f"Processing {batch_file}...")
        summaries = load_summaries(batch_file)
        embed_and_store_in_batches(collection, summaries, batch_size=100, resume=True)
        total_books += len(summaries)
    print(f"Finished inserting {total_books} books from batch {start} to {end-1} into ChromaDB.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed and store book summaries in ChromaDB.")
    parser.add_argument('--start', type=int, default=152,
                        help='Start index of batch files to process')
    parser.add_argument('--end', type=int, default=None,
                        help='End index (exclusive) of batch files to process')
    args = parser.parse_args()
    main(start=args.start, end=args.end)
