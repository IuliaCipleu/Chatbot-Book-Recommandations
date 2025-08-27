import chromadb
import oracledb
from dotenv import load_dotenv
import os

load_dotenv()
DB_CONN_STRING = os.environ.get("DB_CONN_STRING")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("books")

conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_CONN_STRING)
cur = conn.cursor()

for doc in collection.get(include=["metadatas"])['metadatas']:
    if doc and 'title' in doc:
        title = doc['title']
        cur.execute("SELECT book_id FROM books WHERE LOWER(title) = LOWER(:1)", (title,))
        if not cur.fetchone():
            print(f"Inserting: {title}")
            cur.execute("INSERT INTO books (title) VALUES (:1)", (title,))
            conn.commit()

cur.close()
conn.close()
print("Sync complete.")