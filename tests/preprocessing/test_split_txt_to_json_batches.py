import os
import json
import tempfile
from preprocessing.split_txt_to_json_batches import split_txt_to_json_batches

def make_sample_txt(lines):
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    return path

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_split_creates_correct_number_of_batches(tmp_path):
    # 250 valid books, each with unique genre, so 250 files (one per genre)
    lines = [
        f"{i}\t/fb{i}\tBook{i}\tAuthor{i}\t2000\tGenre{i}\tSummary{i}"
        for i in range(250)
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=100)
    files = sorted(os.listdir(out_dir))
    # Each file should be named by genre
    assert all(f.startswith("book_summaries_") and f.endswith(".json") for f in files)
    # There should be 250 files (one per genre)
    assert len(files) == 250
    # Each file should contain one book with correct genre
    for f in files:
        data = read_json(os.path.join(out_dir, f))
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["genre"][0].replace(" ", "_") in f
    os.remove(txt_path)

def test_split_skips_incomplete_and_empty_lines(tmp_path):
    lines = [
        "1\t/fb1\tBook1\tAuthor1\t2000\tGenre1\tSummary1",
        "2\t/fb2\tBook2\tAuthor2\t2001\tGenre2",  # incomplete
        "3\t/fb3\t\tAuthor3\t2002\tGenre3\tSummary3",  # missing title
        "4\t/fb4\tBook4\tAuthor4\t2003\tGenre4\t",  # missing summary
        "",  # empty line
        "5\t/fb5\tBook5\tAuthor5\t2004\tGenre5\tSummary5"
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=2)
    files = sorted(os.listdir(out_dir))
    # Only valid books (Book1, Book5) should be present, each in their genre file
    assert len(files) == 2
    found_titles = set()
    for f in files:
        data = read_json(os.path.join(out_dir, f))
        assert isinstance(data, list)
        assert len(data) == 1
        found_titles.add(data[0]["title"])
    assert found_titles == {"Book1", "Book5"}
    os.remove(txt_path)

def test_split_handles_exact_batch(tmp_path):
    # 4 books, each with unique genre, so 4 files
    lines = [
        f"{i}\t/fb{i}\tBook{i}\tAuthor{i}\t2000\tGenre{i}\tSummary{i}"
        for i in range(4)
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=2)
    files = sorted(os.listdir(out_dir))
    assert len(files) == 4
    for f in files:
        data = read_json(os.path.join(out_dir, f))
        assert isinstance(data, list)
        assert len(data) == 1
    os.remove(txt_path)

def test_split_creates_output_dir(tmp_path):
    lines = [
        "1\t/fb1\tBook1\tAuthor1\t2000\tGenre1\tSummary1"
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "new_batches"
    assert not os.path.exists(out_dir)
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=1)
    assert os.path.exists(out_dir)
    files = os.listdir(out_dir)
    assert len(files) == 1
    # File should be named by genre
    assert files[0].startswith("book_summaries_") and files[0].endswith(".json")
    os.remove(txt_path)

def test_split_empty_input_file(tmp_path):
    txt_path = make_sample_txt([])
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=10)
    assert os.path.exists(out_dir)
    assert os.listdir(out_dir) == []
    os.remove(txt_path)
