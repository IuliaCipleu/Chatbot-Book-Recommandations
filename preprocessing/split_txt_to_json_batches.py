"""
Splits a large book summaries .txt file into multiple JSON files, each containing up to
batch_size books.
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
    batch = {}
    batch_num = 1
    with open(txt_file_path, "r", encoding="utf-8") as f:
        for _, line in enumerate(f, 1):
            parts = line.strip().split("\t")
            if len(parts) < 7:
                continue
            title = parts[2]
            summary = parts[6]
            if not (title and summary):
                continue
            batch[title] = summary
            if len(batch) == batch_size:
                out_path = os.path.join(output_dir, f"book_summaries_batch_{batch_num}.json")
                with open(out_path, "w", encoding="utf-8") as out:
                    json.dump(batch, out, indent=2, ensure_ascii=False)
                print(f"Saved {len(batch)} books to {out_path}")
                batch = {}
                batch_num += 1
        # Save any remaining books
        if batch:
            out_path = os.path.join(output_dir, f"book_summaries_batch_{batch_num}.json")
            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(batch, out, indent=2, ensure_ascii=False)
            print(f"Saved {len(batch)} books to {out_path}")

if __name__ == "__main__":
    split_txt_to_json_batches(
        txt_file_path="data/booksummaries.txt",
        output_dir="data/batches",
        batch_size=100
    )
