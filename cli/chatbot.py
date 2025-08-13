"""
Command-line chatbot for book recommendations using RAG (Retrieval-Augmented Generation), OpenAI,
and ChromaDB.
Supports language selection, voice input, content filtering, and image generation.
"""
import sys
import os

import chromadb
import openai
from search.retriever import search_books
from search.summary_tool import get_summary_by_title
from utils.openai_config import load_openai_key
from utils.image_generator import generate_image_from_summary
from utils.voice_input import listen_with_whisper
from utils.filter import is_appropriate, EXCLUSION_KEYWORDS, infer_reader_profile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("books")


def translate(text, target_language):
    """
    Translates the given text to Romanian using the OpenAI GPT model, preserving the original meaning and style.

    Args:
        text (str): The text to be translated.
        target_language (str): The target language for translation. If set to "english", the original text is returned.

    Returns:
        str: The translated text in Romanian, or the original text if the target language is English.
    """
    if target_language == "english":
        return text
    prompt = f"Translate the following text to Romanian, preserving meaning and style.\n\nText: {text}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def main():
    """
    Main function for the chatbot CLI application.
    This function initializes the chatbot, handles language selection (English or Romanian),
    and manages the main interaction loop with the user. It supports both text and voice input,
    translates queries if necessary, infers the reader's profile, searches for appropriate book
    recommendations, and displays the results (including translated summaries and generated images).
    The function continues to prompt the user for new queries until the user types 'exit'.
    Steps performed:
    1. Loads the OpenAI API key.
    2. Prompts the user to select a language.
    3. Repeatedly asks the user for book preferences (via text or voice).
    4. Translates input to English if Romanian is selected.
    5. Infers the reader's profile and clarifies if needed.
    6. Searches for suitable book recommendations, filtering by appropriateness.
    7. Displays the recommended book and summary, translating back to Romanian if needed.
    8. Generates and displays an image based on the book summary.
    9. Exits when the user types 'exit'.
    """
    load_openai_key()

    # Language selection
    language = ""
    while language not in ["english", "romanian"]:
        language = input("Choose your language (english/romanian): ").strip().lower()

    while True:
        prompt = "What kind of book are you looking for? (type 'exit' to quit): "
        if language == "romanian":
            prompt = "Ce fel de carte cauți? (scrie 'exit' pentru a ieși): "

        use_voice = input("Do you want to use voice input? (yes/no): ").strip().lower() == "yes"

        if use_voice:
            lang_code = "ro" if language == "romanian" else "en"
            try:
                user_input = listen_with_whisper(language=lang_code)
            except Exception as e:
                print(f"Whisper failed: {e}")
                
        else:
            user_input = input(prompt)

        if user_input.lower() == "exit":
            break

        query = user_input
        if language == "romanian":
            query = translate(user_input, "english")

        # STEP 1: Infer reader role
        role = infer_reader_profile(user_input)
        if role not in EXCLUSION_KEYWORDS:
            clarify_prompt = "Who is the book for? (child, teen, adult, technical): "
            if language == "romanian":
                clarify_prompt = "Pentru cine este cartea? (child, teen, adult, technical): "
            role = input(clarify_prompt).strip().lower()
            if role not in EXCLUSION_KEYWORDS:
                role = "adult"  # fallback

        # STEP 2: Search & filter recommendations
        found = False
        top_k = 1
        max_k = 100
        while not found and top_k <= max_k:
            results = search_books(query, collection, top_k=top_k)
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            for idx, _ in enumerate(ids):
                title = metadatas[idx]["title"]
                summary = get_summary_by_title(title)
                if summary and summary.strip() and is_appropriate(summary, role):
                    found = True
                    break
            if not found:
                top_k += 1

        if not found:
            msg = "No book with summary found."
            if language == "romanian":
                msg = "Nu am găsit nicio carte cu rezumat potrivit."
            print(msg)
            continue

        # STEP 3: Display result + translated summary
        if language == "romanian":
            title = translate(title, "romanian")
            summary = translate(summary, "romanian")
            print(f"\nCarte recomandată: {title}")
            print(f"\nRezumat:\n{summary}\n")
        else:
            print(f"\nRecommended Book: {title}")
            print(f"\nSummary:\n{summary}\n")

        # STEP 4: Generate image
        image_url = generate_image_from_summary(title, summary)
        if image_url:
            if language == "romanian":
                print(f"Imagine generată: {image_url}")
            else:
                print(f"Generated Image: {image_url}")


if __name__ == "__main__":
    main()
