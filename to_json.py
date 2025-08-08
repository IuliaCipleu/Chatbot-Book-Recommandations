import json

def parse_cmu_book_summary(txt_file_path, output_json_path, max_books=1000):
    """
    Parses the CMU Book Summary Dataset and creates a JSON mapping from book titles to summaries.
    Only includes books with non-empty titles and summaries.
    """
    book_dict = {}

    with open(txt_file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Each line is tab-separated and contains multiple fields
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue  # skip malformed lines

            wiki_id = parts[0]
            freebase_id = parts[1]
            title = parts[2]
            author = parts[3]
            publication_date = parts[4]
            genres = parts[5]
            summary = parts[6]

            if title and summary:
                # Store as title -> summary
                book_dict[title] = summary

            if len(book_dict) >= max_books:
                break

    # Write to JSON
    with open(output_json_path, "w", encoding="utf-8") as json_out:
        json.dump(book_dict, json_out, indent=2, ensure_ascii=False)
        

    print(f"Saved {len(book_dict)} book summaries to {output_json_path}")

# Example usage:
parse_cmu_book_summary("dataset/booksummaries.txt", "dataset/book_summaries.json", max_books=16559)
