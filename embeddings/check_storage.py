import chromadb

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "books"

client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)
result = collection.get()
print("Number of books stored:", len(result.get("ids", [])))
