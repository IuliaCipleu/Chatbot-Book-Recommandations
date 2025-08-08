"""
This script parses the CMU Book Summary Dataset and creates a JSON mapping from book
titles to summaries.
"""
import json

def parse_cmu_book_summary(txt_file_path, output_json_path, max_books=1000):
    """
    Parses the CMU Book Summary Dataset and creates a JSON mapping from book titles to summaries.
    Ensures at least one book from each genre is included.
    """
    book_dict = {}
    genre_covered = set()
    all_genres = set()

    # First pass: collect all genres
    with open(txt_file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue
            genres = parts[5]
            if genres:
                for genre in genres.split(","):
                    all_genres.add(genre.strip())

    # Second pass: pick at least one book per genre
    with open(txt_file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue
            title = parts[2]
            summary = parts[6]
            genres = parts[5]
            if not (title and summary and genres):
                continue
            for genre in genres.split(","):
                genre = genre.strip()
                if genre and genre not in genre_covered:
                    book_dict[title] = summary
                    genre_covered.add(genre)
                    break  # Only need to add the book once
            if len(genre_covered) == len(all_genres) or len(book_dict) >= max_books:
                break

    # Write to JSON
    with open(output_json_path, "w", encoding="utf-8") as json_out:
        json.dump(book_dict, json_out, indent=2, ensure_ascii=False)

    print(f"Saved {len(book_dict)} book summaries to {output_json_path} (at least one per genre)")

# Example usage:
parse_cmu_book_summary("data/booksummaries.txt", "data/book_summaries.json", max_books=100)
