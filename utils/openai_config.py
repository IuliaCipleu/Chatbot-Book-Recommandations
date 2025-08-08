"""
This module provides a utility function to load the OpenAI API key from the environment and set it
for the OpenAI client.
"""
import os
import openai

def load_openai_key():
    """
    Loads the OpenAI API key from the environment variable 'OPENAI_API_KEY' and sets it
    for the OpenAI client.

    Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")
    openai.api_key = api_key
