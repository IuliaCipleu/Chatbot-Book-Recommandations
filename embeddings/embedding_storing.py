"""
Embeds book summaries using OpenAI and stores them in a ChromaDB collection.

This script loads book summaries from a JSON file, generates embeddings for each summary
using the OpenAI API, and stores the embeddings along with metadata in a ChromaDB database.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import openai
import chromadb
from utils.openai_config import load_openai_key

DATA_PATH = "data/book_summaries.json"
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

def embed_and_store(collection, summaries):
    """
    Generates embeddings for each book summary and stores them in the ChromaDB collection.

    Args:
        collection (chromadb.api.models.Collection.Collection): The ChromaDB collection
        to store embeddings.
        summaries (dict): Dictionary mapping book titles to summaries.
    """
    allowed_models = [
        "text-embedding-4o-mini",
        "text-embedding-4.1-mini",
        "text-embedding-4.1-nano"
    ]
    embedding_model = "text-embedding-4o-mini"  # Default, change as needed

    if embedding_model not in allowed_models:
        raise ValueError(f"Embedding model '{embedding_model}' is not allowed. Allowed models: {allowed_models}")

    for title, summary in summaries.items():
        input_text = f"{title}: {summary}"
        response = openai.embeddings.create(
            input=input_text,
            model=embedding_model
        )
        embedding = response.data[0].embedding
        collection.add(
            documents=[input_text],
            embeddings=[embedding],
            metadatas=[{"title": title}],
            ids=[title]
        )

def main():
    """
    Main function to load API key, initialize ChromaDB, load summaries, and store embeddings.
    """
    load_openai_key()  # Check and set API key
    collection = init_chroma()
    summaries = load_summaries(DATA_PATH)
    embed_and_store(collection, summaries)
    print(f"Finished inserting {len(summaries)} books into ChromaDB.")

if __name__ == "__main__":
    main()
