
from fastapi import Body
import openai
from search.retriever import search_books
from search.summary_tool import get_summary_by_title
from utils.openai_config import load_openai_key
from utils.voice_input import listen_with_whisper
from utils.image_generator import generate_image_from_summary
from utils.filter import is_appropriate, infer_reader_profile, sanitize_for_image_prompt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import chromadb
import httpx


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
    role = data.get("role")
    if not role:
        # Infer user profile from the query
        role = infer_reader_profile(query)
        if role not in ["child", "teen", "adult", "technical"]:
            # Only ask for clarification if query is empty or obviously ambiguous
            if not query or not query.strip():
                language = data.get("language", "english")
                clarify_prompt = "Who is the book for? (child, teen, adult, technical): "
                if language == "romanian":
                    clarify_prompt = "Pentru cine este cartea? (child, teen, adult, technical): "
                return {"clarify_role": True, "prompt": clarify_prompt}
            # Otherwise, fallback to adult for compatibility
            role = "adult"
    language = data.get("language", "english")
    results = search_books(query, collection, top_k=5)
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    for idx, _ in enumerate(ids):
        title = metadatas[idx]["title"]
        summary = get_summary_by_title(title)
        if summary and summary.strip() and summary != "Summary not found." and is_appropriate(summary, role):
            image_url = metadatas[idx].get("image_url")
            if not image_url:
                # Translate to English if needed
                if language == "romanian":
                    async with httpx.AsyncClient() as client:
                        resp_title = await client.post("http://localhost:8000/translate", json={"text": title, "target_lang": "english"})
                        title_en = resp_title.json().get("translated", title)
                        resp_summary = await client.post("http://localhost:8000/translate", json={"text": summary, "target_lang": "english"})
                        summary_en = resp_summary.json().get("translated", summary)
                else:
                    title_en = title
                    summary_en = summary
                # Sanitize summary for DALL·E prompt
                sanitized_summary = sanitize_for_image_prompt(summary_en)
                # Add user type context to the image prompt
                image_prompt = sanitized_summary
                if role == "child":
                    image_prompt += " (colorful, cartoonish, friendly, for children, illustration style)"
                elif role == "teen":
                    image_prompt += " (dynamic, modern, appealing to teenagers, graphic novel style)"
                elif role == "technical":
                    image_prompt += " (clean, schematic, technical illustration, informative)"
                # For adult, no extra style needed
                image_url = generate_image_from_summary(title_en, image_prompt)
                if image_url:
                    collection.update(
                        ids=[title],
                        metadatas=[{**metadatas[idx], "image_url": image_url}]
                    )
            return {"title": title, "summary": summary, "image_url": image_url}
    return {"error": "No suitable book found."}

@app.post("/voice")
async def voice(request: Request):
    data = await request.json()
    language = data.get("language", "english")
    # Map frontend language to whisper language code
    lang_code = "ro" if language == "romanian" else "en"
    text = listen_with_whisper(language=lang_code)
    return JSONResponse({"text": text})

@app.post("/translate")
async def translate(request: Request):
    data = await request.json()
    text = data.get("text")
    target_lang = data.get("target_lang", "romanian")
    if not text:
        return JSONResponse({"translated": ""})
    if target_lang == "romanian":
        prompt = f"Translate the following text to Romanian. Only return the translated text.\n\n{text}"
    else:
        prompt = f"Translate the following text to English. Only return the translated text.\n\n{text}"
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        translated = response.choices[0].message.content.strip()
        return JSONResponse({"translated": translated})
    except Exception as e:
        return JSONResponse({"translated": text, "error": str(e)})
