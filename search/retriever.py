"""
This module provides a function to search for relevant books in a ChromaDB collection using OpenAI
embeddings.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openai
from utils.openai_config import load_openai_key


def search_books(query, collection, top_k=1, model="text-embedding-3-small"):
    """
    Searches for books in the ChromaDB collection that are most relevant to the user's query.

    Args:
        query (str): The user's search query.
        collection: The ChromaDB collection object to search in.
        top_k (int, optional): The number of top results to return. Defaults to 1.
        model (str, optional): The OpenAI embedding model to use.
        Defaults to "text-embedding-3-small".

    Returns:
        dict: The search results from the ChromaDB collection.
    """
    # Ensure the OpenAI API key is set
    if not openai.api_key:
        load_openai_key()
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set.")

    # Use the new OpenAI API for embeddings (openai>=1.0.0)
    response = openai.embeddings.create(
        input=query,
        model=model
    )
    embedding = response.data[0].embedding

    # ChromaDB's query method may expect 'query_embeddings' or 'query_vector'
    return collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
