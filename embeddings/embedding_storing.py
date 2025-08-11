"""
Embeds book summaries using OpenAI and stores them in a ChromaDB collection.

This script loads book summaries from a JSON file, generates embeddings for each summary
using the OpenAI API, and stores the embeddings along with metadata in a ChromaDB database.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import glob
import openai
import chromadb
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
    Loads book summaries from a JSON file.
    Args:
        path (str): Path to the JSON file containing book summaries.
    Returns:
        dict: A dictionary mapping book titles to summaries.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_batch_files(batches_dir):
    """
    Returns a sorted list of all JSON batch files in the given directory.
    """
    return sorted(glob.glob(os.path.join(batches_dir, "book_summaries_batch_*.json")))

def embed_and_store_in_batches(collection, summaries, batch_size=100, resume=True, embedding_model="text-embedding-3-small"):
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

    items = list(summaries.items())
    total = len(items)
    i = 0
    while i < total:
        batch = []
        batch_titles = []
        batch_ids = []
        batch_metas = []
        for j in range(i, min(i+batch_size, total)):
            title, summary = items[j]
            if resume and title in existing_ids:
                continue
            input_text = f"{title}: {summary}"
            batch.append(input_text)
            batch_titles.append(title)
            batch_ids.append(title)
            batch_metas.append({"title": title})
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

def main():
    """
    Main function to load API key, initialize ChromaDB, load summaries, and store embeddings.
    """
    load_openai_key()  # Check and set API key
    collection = init_chroma()
    batch_files = get_all_batch_files(BATCHES_DIR)
    total_books = 0
    for batch_file in batch_files:
        print(f"Processing {batch_file}...")
        summaries = load_summaries(batch_file)
        embed_and_store_in_batches(collection, summaries, batch_size=100, resume=True)
        total_books += len(summaries)
    print(f"Finished inserting {total_books} books from all batches into ChromaDB.")

if __name__ == "__main__":
    main()
