"""
Checks the number of book entries stored in the ChromaDB collection.
Useful for verifying persistent storage and collection status.
"""
import chromadb

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "books"

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)
result = collection.get()
print("Number of books stored:", len(result.get("ids", [])))
# Number of books stored: 11901
