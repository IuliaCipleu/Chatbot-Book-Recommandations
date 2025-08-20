"""
This module provides a utility function to load the OpenAI API key from the environment and set it
for the OpenAI client.
"""
import os
import openai
from dotenv import load_dotenv

def load_openai_key():
    """
    Loads the OpenAI API key from the environment variable 'OPENAI_API_KEY' and sets it
    for the OpenAI client. If the key is not valid, attempts to reload from .env.
    Prints both the original and .env-loaded key values for debugging.

    Raises:
        ValueError: If the 'OPENAI_API_KEY' environment variable is not set or invalid.
    """
    env_key = os.getenv("OPENAI_API_KEY")
    print(f"OPENAI_API_KEY from environment: {env_key}")
    load_dotenv(override=True)
    dotenv_key = os.environ.get("OPENAI_API_KEY")
    print(f"OPENAI_API_KEY from .env after load_dotenv: {dotenv_key}")
    api_key = dotenv_key
    if not api_key or not api_key.startswith("sk-"):
        raise ValueError("OPENAI_API_KEY not set or invalid in environment or .env file.")
    openai.api_key = api_key.strip()
