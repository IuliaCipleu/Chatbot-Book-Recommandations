import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chromadb
from search.retriever import search_books
from search.summary_tool import get_summary_by_title
from utils.openai_config import load_openai_key
from utils.image_generator import generate_image_from_summary
from utils.voice_input import listen_to_microphone
import openai

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("books")

EXCLUSION_KEYWORDS = {
    "child": {"violence", "drugs", "sex", "death", "abuse"},
    "teen": {"graphic sex", "heavy violence"},
    "technical": {"fairy tale", "fantasy", "magic"},
    "adult": set(),
}


def translate(text, target_language):
    if target_language == "english":
        return text
    prompt = f"Translate the following text to Romanian, preserving meaning and style.\n\nText: {text}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def infer_reader_profile(user_input: str) -> str:
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


def is_appropriate(summary, profile):
    banned = EXCLUSION_KEYWORDS.get(profile, set())
    return not any(word in summary.lower() for word in banned)


def main():
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
            user_input = listen_to_microphone(language="ro-RO" if language == "romanian" else "en-US")
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
            for idx, book_id in enumerate(ids):
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
                print(f"📷 Imagine generată: {image_url}")
            else:
                print(f"📷 Generated Image: {image_url}")


if __name__ == "__main__":
    main()
