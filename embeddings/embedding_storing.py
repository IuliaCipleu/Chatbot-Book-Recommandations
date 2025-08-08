import os
import json
import openai
import chromadb
from chromadb.config import Settings

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OPENAI_API_KEY is set.")
else:
    print("OPENAI_API_KEY is not set.")

# 1. Setup ChromaDB
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
collection = chroma_client.get_or_create_collection("books")

# 2. Load summaries
with open("book_summaries.json", "r", encoding="utf-8") as f:
    summaries = json.load(f)

# 3. Add to ChromaDB with embeddings
for title, summary in summaries.items():
    input_text = f"{title}: {summary}"

    response = openai.Embedding.create(
        input=input_text,
        model="text-embedding-3-small"
    )
    embedding = response['data'][0]['embedding']

    collection.add(
        documents=[input_text],
        embeddings=[embedding],
        metadatas=[{"title": title}],
        ids=[title]
    )

print("Finished inserting books into ChromaDB.")
