# Smart Librarian Chatbot

An AI book recommender using OpenAI + ChromaDB (RAG).

## Features
- Recommend books based on user themes
- Detailed summaries (via local tool)
- CLI Interface (Streamlit/React planned)
- Optional: language filter, TTS, image generation

## Dataset
This project uses the [CMU Book Summary Dataset](https://www.kaggle.com/datasets/ymaricar/cmu-book-summary-dataset) available on Kaggle.

## Project Structure
- `cli/`: command line interface
- `data/`: summaries & inputs
- `search/`: semantic search & summary tool
...

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set `OPENAI_API_KEY` as env variable
3. Run: `python embeddings/embedding_storing.py`
