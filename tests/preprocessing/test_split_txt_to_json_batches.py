import os
import json
import tempfile
import shutil
import pytest
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
    # 250 valid books, batch_size=100 -> 3 batches (100, 100, 50)
    lines = [
        f"{i}\t/fb{i}\tBook{i}\tAuthor{i}\t2000\tGenre{i}\tSummary{i}"
        for i in range(250)
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=100)
    files = sorted(os.listdir(out_dir))
    assert len(files) == 3
    assert all(f.startswith("book_summaries_batch_") for f in files)
    # Check counts
    counts = [len(read_json(os.path.join(out_dir, f))) for f in files]
    assert counts == [100, 100, 50]
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
    assert len(files) == 1
    data = read_json(os.path.join(out_dir, files[0]))
    assert set(data.keys()) == {"Book1", "Book5"}
    os.remove(txt_path)

def test_split_handles_exact_batch(tmp_path):
    # 4 books, batch_size=2 -> 2 batches of 2
    lines = [
        f"{i}\t/fb{i}\tBook{i}\tAuthor{i}\t2000\tGenre{i}\tSummary{i}"
        for i in range(4)
    ]
    txt_path = make_sample_txt(lines)
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=2)
    files = sorted(os.listdir(out_dir))
    assert len(files) == 2
    for f in files:
        data = read_json(os.path.join(out_dir, f))
        assert len(data) == 2
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
    os.remove(txt_path)

def test_split_empty_input_file(tmp_path):
    txt_path = make_sample_txt([])
    out_dir = tmp_path / "batches"
    split_txt_to_json_batches(txt_path, str(out_dir), batch_size=10)
    assert os.path.exists(out_dir)
    assert os.listdir(out_dir) == []
    os.remove(txt_path)