from search.retriever import search_books
from search.summary_tool import get_summary_by_title
from chromadb.config import Settings
import chromadb

# Initialize ChromaDB client
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
collection = client.get_or_create_collection("books")

# Main loop
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
