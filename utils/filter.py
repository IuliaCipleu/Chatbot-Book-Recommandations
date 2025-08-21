"""
This module provides utilities for filtering offensive content from text using a configurable list
of bad words.
"""
import json
import string
import re
from typing import Tuple
import openai
from search.summary_tool import get_summary_by_title

from utils.openai_config import load_openai_key

# Exclusion keywords for user type filtering
EXCLUSION_KEYWORDS = {
    "child": {"violence", "drugs", "sex", "death", "abuse"},
    "teen": {"graphic sex", "heavy violence"},
    "technical": {"fairy tale", "fantasy", "magic"},
    "adult": set(),
}

BOOK_PATTERNS = [
    r"\bbook(s)?\b",
    r"\bnovel(s)?\b",
    r"\bstory(?:|ies)\b",
    r"\bauthor(s)?\b",
    r"\bgenre(s)?\b",
    r"\bread(ing)?\b",
    r"\brecommend(ed|ation|ations)?\b",
    r"\bliterature\b",
    r"\btale(s)?\b",
    r"\bseries\b",
    r"\blibrary\b",
    r"\bchapter(s)?\b",
    r"\bplot\b",
    r"\bsummary\b",
]

# Simple subject extractors: grabs text after common “about/on/regarding …” patterns,
# otherwise uses the input (trimmed).
SUBJECT_REGEXES = [
    re.compile(r".*?\babout\b\s+(?P<subj>.+)", re.IGNORECASE | re.DOTALL),
    re.compile(r".*?\bon\b\s+(?P<subj>.+)", re.IGNORECASE | re.DOTALL),
    re.compile(r".*?\bregarding\b\s+(?P<subj>.+)", re.IGNORECASE | re.DOTALL),
    re.compile(r".*?\brelated to\b\s+(?P<subj>.+)", re.IGNORECASE | re.DOTALL),
]

def is_appropriate(summary, profile):
    """
    Determines if a book summary is appropriate for a given user profile by checking for the
    presence of banned keywords.

    Args:
        summary (str): The summary text of the book to be evaluated.
        profile (str): The user profile used to retrieve the set of exclusion keywords.

    Returns:
        bool: True if the summary does not contain any banned keywords for the profile,
        False otherwise.
    """
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
    to classify the intended reader into one of the following categories: 'child',
    'teen', 'adult', or 'technical'.
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

    # Remove quotes and special characters
    sanitized = text.replace('"', '').replace("'", "")
    sanitized = re.sub(r'[^\w\s,.!?-]', '', sanitized)
    # Remove bad words
    for bad in BAD_WORDS:
        sanitized = re.sub(rf'\\b{re.escape(bad)}\\b', '[filtered]', sanitized, flags=re.IGNORECASE)
    # Remove explicit/triggering phrases (basic)
    sanitized = re.sub(r'(sex|violence|abuse|drugs|death)', '[filtered]', sanitized,
                       flags=re.IGNORECASE)
    # Truncate
    if len(sanitized) > 300:
        sanitized = sanitized[:297] + '...'
    return sanitized

# Prefer books similar to those highly rated by the user (improved: genre/author/theme via
# summary keyword overlap)
def is_similar_to_high_rated(meta, high_rated_books):
    """
    meta: metadata dict for candidate book
    high_rated_books: list of dicts with keys 'title', 'genre', 'author', 'summary'
    Returns True if candidate is similar to any high rated book by genre, author, or summary theme.
    """
    candidate_genre = meta.get("genre", "").lower() if meta.get("genre") else ""
    candidate_author = meta.get("author", "").lower() if meta.get("author") else ""
    candidate_summary = meta.get("summary", "").lower() if meta.get("summary") else ""
    # Fallback: try to get summary by title if not present
    if not candidate_summary and meta.get("title"):
        try:
            candidate_summary = get_summary_by_title(meta["title"]).lower()
        except Exception:
            candidate_summary = ""

    for b in high_rated_books:
        b_genre = b.get("genre", "").lower() if b.get("genre") else ""
        b_author = b.get("author", "").lower() if b.get("author") else ""
        b_summary = b.get("summary", "").lower() if b.get("summary") else ""
        # Genre or author match
        if candidate_genre and b_genre and candidate_genre == b_genre:
            return True
        if candidate_author and b_author and candidate_author == b_author:
            return True
        # Theme similarity: keyword overlap in summaries
        if candidate_summary and b_summary:
            # Use set of keywords (remove stopwords, short words)
            def keywords(text):
                stopwords = set(["the","a","an","and","of","in","on","to","for","with","by",
                                 "at","from","is","it","as","that","this","was","are","be",
                                 "or","but","if","not","into","their","his","her","its","they",
                                 "them","he","she","you","we","our","your","i"])
                return set(w for w in re.findall(r"\b\w{4,}\b", text) if w not in stopwords)
            cand_kw = keywords(candidate_summary)
            b_kw = keywords(b_summary)
            if cand_kw and b_kw:
                overlap = cand_kw & b_kw
                # If there is significant overlap, consider similar (threshold: 5 words or 20% of
                # candidate keywords)
                if len(overlap) >= 5 or (len(cand_kw) > 0 and len(overlap) / len(cand_kw) > 0.2):
                    return True
    return False

def _looks_book_related(text: str) -> bool:
    return any(re.search(p, text) for p in BOOK_PATTERNS)

def _extract_subject(text: str) -> str:
    cleaned = text.strip()
    for rx in SUBJECT_REGEXES:
        m = rx.match(cleaned)
        if m:
            subj = m.group("subj").strip(" .!?\"'“”‘’")
            if subj:
                return subj
    # Fallback: compress whitespace and trim length
    subj = re.sub(r"\s+", " ", cleaned)
    return (subj[:120] + "…") if len(subj) > 120 else subj

def is_book_related(user_input: str) -> Tuple[bool, str]:
    """
    Returns (is_related, message). If not related, message says:
    "I am only specialized in books, not in subjects like 'X'.
    But if you want I can provide a book related to 'X'."
    """
    text = user_input or ""
    if _looks_book_related(text.lower()):
        return True, ""

    subject = _extract_subject(text)
    msg = (
        f"I am only specialized in books, not in subjects like '{subject}'. "
        f"But if you want I can provide a book related to '{subject}'."
    )
    return False, msg
