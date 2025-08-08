import json

def get_summary_by_title(title, json_path="data/book_summaries.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        summaries = json.load(f)
    return summaries.get(title, "Summary not found.")
