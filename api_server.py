from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from search.retriever import search_books
from search.summary_tool import get_summary_by_title
from utils.openai_config import load_openai_key
from utils.voice_input import listen_with_whisper
from fastapi.responses import JSONResponse
@app.post("/voice")
async def voice(request: Request):
    data = await request.json()
    language = data.get("language", "english")
    # Map frontend language to whisper language code
    lang_code = "ro" if language == "romanian" else "en"
    text = listen_with_whisper(language=lang_code)
    return JSONResponse({"text": text})
import chromadb

app = FastAPI()

# Allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("books")
load_openai_key()

@app.post("/recommend")
async def recommend(request: Request):
    data = await request.json()
    query = data.get("query")
    role = data.get("role", "adult")
    language = data.get("language", "english")
    results = search_books(query, collection, top_k=5)
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    for idx, _ in enumerate(ids):
        title = metadatas[idx]["title"]
        summary = get_summary_by_title(title)
        if summary and summary.strip() and summary != "Summary not found.":
            return {"title": title, "summary": summary}
    return {"error": "No suitable book found."}