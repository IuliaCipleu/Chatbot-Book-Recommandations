"""
This module provides retrieval functionality for a Retrieval-Augmented Generation (RAG) pipeline.
It enables searching for relevant books in a ChromaDB vector database using OpenAI embeddings.
The retrieved results can be used as context for generative models to enhance book recommendations
or responses.
"""
import sys
import os
import openai
from utils.openai_config import load_openai_key
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def search_books(query, collection, top_k=1, model="text-embedding-3-small"):
    """
    Retrieves the most relevant books from the ChromaDB vector database for a given user query
    using OpenAI embeddings. This function is the retrieval step in a Retrieval-Augmented
    Generation (RAG) workflow, where the retrieved documents can be provided as context to a
    language model for enhanced, context-aware responses or recommendations.

    Args:
        query (str): The user's search query.
        collection: The ChromaDB collection object to search in.
        top_k (int, optional): The number of top results to return. Defaults to 1.
        model (str, optional): The OpenAI embedding model to use.
        Defaults to "text-embedding-3-small".

    Returns:
        dict: The search results from the ChromaDB collection, suitable for use as context in a
        RAG pipeline.
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
