"""
Command-line chatbot for book recommendations.

This script interacts with the user, retrieves book recommendations based on user input,
and displays the recommended book's title and summary using ChromaDB and custom search utilities.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import chromadb
from search.retriever import search_books
from search.summary_tool import get_summary_by_title
import openai

# Initialize ChromaDB client (new API)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("books")

def translate(text, target_language):
    """
    Translate text to the target language using OpenAI's GPT model.
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
    Runs the main chatbot loop, prompting the user for book preferences,
    searching for recommendations, and displaying results.
    """
    # Language selection
    language = ""
    while language not in ["english", "romanian"]:
        language = input("Choose your language (english/romanian): ").strip().lower()

    while True:
        prompt = "What kind of book are you looking for? (type 'exit' to quit): "
        if language == "romanian":
            prompt = "Ce fel de carte cauți? (scrie 'exit' pentru a ieși): "
        user_input = input(prompt)
        if user_input.lower() == "exit":
            break

        query = user_input
        if language == "romanian":
            # Translate Romanian input to English for search
            query = translate(user_input, "english")

        found = False
        top_k = 1
        max_k = 100  # Try up to 10 results
        while not found and top_k <= max_k:
            results = search_books(query, collection, top_k=top_k)
            ids = results["ids"][0]
            metadatas = results["metadatas"][0]
            for idx, book_id in enumerate(ids):
                title = metadatas[idx]["title"]
                summary = get_summary_by_title(title)
                if summary and summary.strip():
                    found = True
                    break
            if not found:
                top_k += 1

        if not found:
            msg = "No book with summary found."
            if language == "romanian":
                msg = "Nu am găsit nicio carte cu rezumat."
            print(msg)
            continue

        if language == "romanian":
            title = translate(title, "romanian")
            summary = translate(summary, "romanian")
            print(f"\nCarte recomandată: {title}")
            print(f"\nRezumat:\n{summary}\n")
        else:
            print(f"\nRecommended Book: {title}")
            print(f"\nSummary:\n{summary}\n")

if __name__ == "__main__":
    main()
