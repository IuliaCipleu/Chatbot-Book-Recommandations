from unittest.mock import patch, MagicMock
import builtins
import pytest

import cli.chatbot as chatbot

@pytest.fixture(autouse=True)
def patch_openai(monkeypatch):
    # Patch openai.chat.completions.create to return a mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="adult"))]
    monkeypatch.setattr("openai.chat.completions.create", lambda *a, **kw: mock_response)
    yield

def test_translate_english_returns_original():
    assert chatbot.translate("Hello", "english") == "Hello"

def test_translate_romanian_calls_openai(monkeypatch):
    called = {}
    def fake_create(**kwargs):
        called["prompt"] = kwargs["messages"][0]["content"]
        class Resp:
            choices = [type("C", (), {"message": type("M", (), {"content": "Salut"})()})()]
        return Resp()
    monkeypatch.setattr("openai.chat.completions.create", fake_create)
    result = chatbot.translate("Hello", "romanian")
    assert result == "Salut"
    assert "Translate the following text to Romanian" in called["prompt"]

def test_infer_reader_profile_returns_lower(monkeypatch):
    def fake_create(**kwargs):
        class Resp:
            choices = [type("C", (), {"message": type("M", (), {"content": "Teen"})()})()]
        return Resp()
    monkeypatch.setattr("openai.chat.completions.create", fake_create)
    assert chatbot.infer_reader_profile("A book for teens") == "teen"

def test_is_appropriate_blocks_banned():
    assert not chatbot.is_appropriate("This book contains violence and abuse.", "child")
    assert chatbot.is_appropriate("A technical manual.", "child")

def test_is_appropriate_no_banned_for_adult():
    assert chatbot.is_appropriate("This book contains violence and sex.", "adult")

def test_main_flow_text(monkeypatch):
    # Patch all I/O and OpenAI calls for a full flow
    inputs = iter([
        "english",  # language
        "no",       # voice input
        "A book for a child about courage",  # user input
        "exit"      # exit
    ])
    def fake_input(*args, **kwargs):
        try:
            return next(inputs)
        except StopIteration:
            return "exit"  # Always exit if more input is requested

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr(chatbot, "load_openai_key", lambda: None)
    monkeypatch.setattr(chatbot, "infer_reader_profile", lambda x: "child")
    monkeypatch.setattr(chatbot, "search_books", lambda q, c, top_k=1: {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Brave Little Girl"}]]
    })
    monkeypatch.setattr(chatbot, "get_summary_by_title", lambda t:
        "A story about courage and kindness.")
    monkeypatch.setattr(chatbot, "generate_image_from_summary", lambda t, s:
        "http://img.com/cover.png")
    monkeypatch.setattr(chatbot, "translate", lambda t, lang: t)
    # Patch print to capture output
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *a, **k: printed.append(" ".join(map(str, a))))
    chatbot.main()
    assert any("Recommended Book: Brave Little Girl" in line for line in printed)
    assert any("Summary:" in line for line in printed)
    assert any("Generated Image: http://img.com/cover.png" in line for line in printed)

def test_main_flow_voice(monkeypatch):
    # Patch all I/O and OpenAI calls for a full flow with voice
    inputs = iter([
        "english",  # language
        "yes",      # voice input
        "exit"      # exit
    ])
    def fake_input(*a, **k):
        try:
            return next(inputs)
        except StopIteration:
            return "exit"
    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(chatbot, "load_openai_key", lambda: None)
    monkeypatch.setattr(chatbot, "listen_with_whisper", lambda **kwargs:
        "A book for a teen about science")
    monkeypatch.setattr(chatbot, "infer_reader_profile", lambda x: "teen")
    monkeypatch.setattr(chatbot, "search_books", lambda q, c, top_k=1: {
        "ids": [["id2"]],
        "metadatas": [[{"title": "Teen Science"}]]
    })
    monkeypatch.setattr(chatbot, "get_summary_by_title", lambda t:
        "A science adventure for teens.")
    monkeypatch.setattr(chatbot, "generate_image_from_summary", lambda t, s:
        "http://img.com/science.png")
    monkeypatch.setattr(chatbot, "translate", lambda t, lang: t)
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *a, **k: printed.append(" ".join(map(str, a))))
    chatbot.main()
    assert any("Recommended Book: Teen Science" in line for line in printed)
    assert any("Generated Image: http://img.com/science.png" in line for line in printed)

def test_main_flow_no_summary(monkeypatch):
    # Patch all I/O and OpenAI calls for a flow with no summary found
    inputs = iter([
        "english",  # language
        "no",       # voice input
        "A book for a child about courage",  # user input
        "exit"      # exit
    ])
    def fake_input(*a, **k):
        try:
            return next(inputs)
        except StopIteration:
            return "exit"
    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(chatbot, "load_openai_key", lambda: None)
    monkeypatch.setattr(chatbot, "infer_reader_profile", lambda x: "child")
    monkeypatch.setattr(chatbot, "search_books", lambda q, c, top_k=1: {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Brave Little Girl"}]]
    })
    monkeypatch.setattr(chatbot, "get_summary_by_title", lambda t: "")
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *a, **k: printed.append(" ".join(map(str, a))))
    chatbot.main()
    assert any("No book with summary found." in line for line in printed)

def test_main_flow_romanian(monkeypatch):
    # Patch all I/O and OpenAI calls for a full flow in Romanian
    inputs = iter([
        "romanian",  # language
        "no",        # voice input
        "O carte pentru copii despre curaj",  # user input
        "exit"       # exit
    ])
    def fake_input(*a, **k):
        try:
            return next(inputs)
        except StopIteration:
            return "exit"
    monkeypatch.setattr(builtins, "input", fake_input)
    monkeypatch.setattr(chatbot, "load_openai_key", lambda: None)
    monkeypatch.setattr(chatbot, "infer_reader_profile", lambda x: "child")
    monkeypatch.setattr(chatbot, "search_books", lambda q, c, top_k=1: {
        "ids": [["id1"]],
        "metadatas": [[{"title": "Fetița Curajoasă"}]]
    })
    monkeypatch.setattr(chatbot, "get_summary_by_title", lambda t: 
        "O poveste despre curaj și bunătate.")
    monkeypatch.setattr(chatbot, "generate_image_from_summary", lambda t, s: 
        "http://img.com/romanian.png")
    monkeypatch.setattr(chatbot, "translate", lambda t, lang: t + " [ro]" if lang == "romanian" else t)
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *a, **k: printed.append(" ".join(map(str, a))))
    chatbot.main()
    assert any("Carte recomandată: Fetița Curajoasă [ro]" in line for line in printed)
    assert any("Rezumat:" in line for line in printed)
    assert any("Imagine generată: http://img.com/romanian.png" in line for line in printed)
    