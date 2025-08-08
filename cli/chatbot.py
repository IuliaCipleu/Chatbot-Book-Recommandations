"""
Command-line chatbot for book recommendations.

This script interacts with the user, retrieves book recommendations based on user input,
and displays the recommended book's title and summary using ChromaDB and custom search utilities.
"""

from chromadb.config import Settings
import chromadb
from search.retriever import search_books
from search.summary_tool import get_summary_by_title

# Initialize ChromaDB client
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
collection = client.get_or_create_collection("books")

def main():
    """
    Runs the main chatbot loop, prompting the user for book preferences,
    searching for recommendations, and displaying results.
    """
    while True:
        user_input = input("What kind of book are you looking for? (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        results = search_books(user_input, collection)
        if not results["ids"][0]:
            print("No book found.")
            continue

        title = results["metadatas"][0][0]["title"]
        print(f"\nRecommended Book: {title}")
        print(f"\nSummary:\n{get_summary_by_title(title)}\n")

if __name__ == "__main__":
    main()
