"""
split_txt_to_json_batches.py

Splits a large book summaries .txt file into multiple genre-based JSON files.

Features:
- Reads tab-separated book summaries from a .txt file
- Extracts title, author, genre(s), and summary for each book
- Groups books by their first listed genre
- Outputs one JSON file per genre, each containing a list of book dicts
- Handles both string and JSON genre formats
- Skips incomplete or invalid lines
- Prints progress for each genre file saved


Recommended to run before embedding_storing.py for ChromaDB ingestion
"""
import json
import os

def split_txt_to_json_batches(txt_file_path, output_dir, batch_size=100):
    """
    Splits a large book summaries .txt file into multiple JSON files, each containing up to
    batch_size books.

    Args:
        txt_file_path (str): Path to the input .txt file with book summaries.
        output_dir (str): Directory where the JSON batch files will be saved.
        batch_size (int, optional): Number of books per batch file. Defaults to 100.
    """
    os.makedirs(output_dir, exist_ok=True)
    genre_batches = {}
    with open(txt_file_path, "r", encoding="utf-8") as f:
        for _, line in enumerate(f, 1):
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue
            title = parts[2]
            author = parts[3] if len(parts) > 3 else None
            genres = parts[5] if len(parts) > 5 else None
            genre_list = None
            if genres:
                try:
                    genre_dict = json.loads(genres)
                    if isinstance(genre_dict, dict):
                        genre_list = list(genre_dict.values())
                except Exception:
                    genre_list = [g.strip() for g in genres.split(",") if g.strip()]
            summary = parts[6]
            if not (title and summary and genre_list and len(genre_list) > 0):
                continue
            first_genre = genre_list[0]
            book = {
                "title": title,
                "summary": summary,
                "genre": genre_list,
                "author": author
            }
            if first_genre not in genre_batches:
                genre_batches[first_genre] = []
            genre_batches[first_genre].append(book)
    # Write one file per genre
    for genre, books in genre_batches.items():
        safe_genre = genre.replace("/", "_").replace(" ", "_")
        out_path = os.path.join(output_dir, f"book_summaries_{safe_genre}.json")
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(books, out, indent=2, ensure_ascii=False)
        print(f"Saved {len(books)} books to {out_path}")

if __name__ == "__main__":
    split_txt_to_json_batches(
        txt_file_path="data/booksummaries.txt",
        output_dir="data/batches",
        batch_size=100
    )
