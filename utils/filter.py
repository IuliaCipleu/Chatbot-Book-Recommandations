"""
This module provides utilities for filtering offensive content from text using a configurable list
of bad words.
"""
import json
import string
import openai

from utils.openai_config import load_openai_key

# Exclusion keywords for user type filtering
EXCLUSION_KEYWORDS = {
    "child": {"violence", "drugs", "sex", "death", "abuse"},
    "teen": {"graphic sex", "heavy violence"},
    "technical": {"fairy tale", "fantasy", "magic"},
    "adult": set(),
}

def is_appropriate(summary, profile):
    banned = EXCLUSION_KEYWORDS.get(profile, set())
    return not any(word in summary.lower() for word in banned)

def load_bad_words(json_path="data/bad_words.json"):
    """
    Loads a list of bad words from a JSON file and returns them as a set.

    Args:
        json_path (str, optional): Path to the JSON file containing bad words.
        Defaults to "data/bad_words.json".

    Returns:
        set: A set of bad words loaded from the file. Returns an empty set if loading fails.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load bad words list: {e}")
        return set()

BAD_WORDS = load_bad_words()

def is_offensive(text):
    """
    Checks if the given text contains any offensive words from the BAD_WORDS set.

    Args:
        text (str): The text to check for offensive content.

    Returns:
        bool: True if any bad word is found in the text, False otherwise.
    """
    words = [w.strip(string.punctuation) for w in text.lower().split()]
    return any(word in words for word in BAD_WORDS)

def infer_reader_profile(user_input: str) -> str:
    """
    Infers the target reader profile category from a given book request.

    Given a user input describing a book request, this function uses an OpenAI language model
    to classify the intended reader into one of the following categories: 'child', 'teen', 'adult', or 'technical'.
    If the category cannot be determined, it returns 'unknown'.

    Args:
        user_input (str): The user's book request or description.

    Returns:
        str: The inferred reader category ('child', 'teen', 'adult', 'technical', or 'unknown').
    """
    load_openai_key()
    
    prompt = (
        "Classify the target reader of this book request into one of the following categories: "
        "child, teen, adult, technical. If uncertain, respond with 'unknown'.\n\n"
        f"Book request: \"{user_input}\"\n\n"
        "Category:"
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().lower()

def sanitize_for_image_prompt(text):
    """
    Sanitize text for image generation prompts:
    - Remove or mask offensive/bad words
    - Remove quotes and special characters
    - Truncate to 300 chars
    - Remove explicit/triggering phrases
    """
    import re
    # Remove quotes and special characters
    sanitized = text.replace('"', '').replace("'", "")
    sanitized = re.sub(r'[^\w\s,.!?-]', '', sanitized)
    # Remove bad words
    for bad in BAD_WORDS:
        sanitized = re.sub(rf'\\b{re.escape(bad)}\\b', '[filtered]', sanitized, flags=re.IGNORECASE)
    # Remove explicit/triggering phrases (basic)
    sanitized = re.sub(r'(sex|violence|abuse|drugs|death)', '[filtered]', sanitized, flags=re.IGNORECASE)
    # Truncate
    if len(sanitized) > 300:
        sanitized = sanitized[:297] + '...'
    return sanitized