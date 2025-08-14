"""
Unit tests for the `listen_with_whisper` function in the `utils.voice_input` module.
These tests cover the following scenarios:
- Successful transcription using Whisper with proper cleanup of temporary audio files.
- Handling exceptions during cleanup (file removal).
- Using monkeypatching to simulate dependencies and file operations.
- Ensuring correct behavior when Whisper returns no transcription text.
- Handling exceptions during the transcription process.
- Handling exceptions during file removal after transcription.
Fixtures and mocking are used to isolate the function from external dependencies such as audio
recording, file I/O, and Whisper model loading.
Tested functions:
- `listen_with_whisper(duration)`: Records audio, saves it to a temporary file, transcribes it
using Whisper, and cleans up the temporary file.
Test utilities:
- `mock_audio`: Simulates silent audio input for testing.
"""

from unittest import mock
import wave
import numpy as np
import pytest

import utils.voice_input as voice_input

@pytest.fixture
def mock_whisper_model():
    """
    Return a mock Whisper model with a transcribe method for testing.
    """
    mock_model = mock.Mock()
    mock_model.transcribe.return_value = {"text": "hello world"}
    return mock_model

@mock.patch("utils.voice_input.whisper.load_model")
@mock.patch("utils.voice_input.sd.rec")
@mock.patch("utils.voice_input.sd.wait")
@mock.patch("utils.voice_input.wave.open")
@mock.patch("utils.voice_input.os.remove")
def test_listen_with_whisper_success(
    mock_remove, mock_wave_open, mock_sd_wait, mock_sd_rec, mock_load_model
):
    """
    Test listen_with_whisper returns correct text and cleans up temp file on success.
    """
    mock_model = mock.Mock()
    mock_model.transcribe.return_value = {"text": "hello world"}
    mock_load_model.return_value = mock_model
    mock_sd_rec.return_value = np.zeros((5 * 16000, 1), dtype=np.float32)
    mock_wave_file = mock.MagicMock()
    mock_wave_open.return_value.__enter__.return_value = mock_wave_file

    result = voice_input.listen_with_whisper(duration=1)
    assert result == "hello world"
    mock_remove.assert_called_once_with("temp_audio.wav")

@mock.patch("utils.voice_input.whisper.load_model")
@mock.patch("utils.voice_input.sd.rec")
@mock.patch("utils.voice_input.sd.wait")
@mock.patch("utils.voice_input.wave.open")
@mock.patch("utils.voice_input.os.remove")
def test_listen_with_whisper_cleanup_exception(
    mock_remove, mock_wave_open, mock_sd_wait, mock_sd_rec, mock_load_model
):
    """
    Test listen_with_whisper returns text even if temp file removal raises an exception.
    """
    mock_model = mock.Mock()
    mock_model.transcribe.return_value = {"text": "cleanup test"}
    mock_load_model.return_value = mock_model
    mock_sd_rec.return_value = np.zeros((5 * 16000, 1), dtype=np.float32)
    mock_wave_file = mock.MagicMock()
    mock_wave_open.return_value.__enter__.return_value = mock_wave_file
    mock_remove.side_effect = Exception("cannot delete file")

    result = voice_input.listen_with_whisper(duration=1)
    assert result == "cleanup test"
    mock_remove.assert_called_once_with("temp_audio.wav")

def mock_audio(**kwargs):
    # Return a numpy array of zeros (simulate silence)
    """
    Simulate silent audio input by returning a numpy array of zeros.
    """
    return np.zeros((int(kwargs.get('samplerate', 16000) * kwargs.get('duration', 5)), 1),
                    dtype='float32')

def test_listen_with_whisper_success_monkeypatch(monkeypatch, tmp_path):
    # Patch dependencies
    """
    Test listen_with_whisper with monkeypatched dependencies for successful transcription.
    """
    dummy_text = "hello world"
    mock_model = mock.MagicMock()
    mock_model.transcribe.return_value = {"text": dummy_text}
    monkeypatch.setattr(voice_input.whisper, "load_model", lambda name: mock_model)
    monkeypatch.setattr(voice_input.sd, "rec", lambda *a, **k: mock_audio(
        duration=a[0]/k['samplerate'],
        samplerate=k['samplerate'])
                        )
    monkeypatch.setattr(voice_input.sd, "wait", lambda: None)
    monkeypatch.setattr(voice_input.os, "remove", lambda path: None)
    # Patch wave.open to use a real file in tmp_path

    orig_wave_open = wave.open
    def fake_wave_open(path, mode):
        # Always use a file in tmp_path
        return orig_wave_open(str(tmp_path / "temp_audio.wav"), mode)
    monkeypatch.setattr(voice_input.wave, "open", fake_wave_open)
    # Run
    result = voice_input.listen_with_whisper(duration=0.01)  # very short
    assert result == dummy_text

def test_listen_with_whisper_no_text(monkeypatch, tmp_path):
    """
    Test listen_with_whisper returns empty string if Whisper returns no transcription text.
    """
    mock_model = mock.MagicMock()
    mock_model.transcribe.return_value = {"not_text": "nope"}
    monkeypatch.setattr(voice_input.whisper, "load_model", lambda name: mock_model)
    monkeypatch.setattr(voice_input.sd, "rec", lambda *a, **k: mock_audio(
        duration=a[0]/k['samplerate'], samplerate=k['samplerate']
        ))
    monkeypatch.setattr(voice_input.sd, "wait", lambda: None)
    monkeypatch.setattr(voice_input.os, "remove", lambda path: None)
    orig_wave_open = wave.open
    def fake_wave_open(path, mode):
        return orig_wave_open(str(tmp_path / "temp_audio.wav"), mode)
    monkeypatch.setattr(voice_input.wave, "open", fake_wave_open)
    result = voice_input.listen_with_whisper(duration=0.01)
    assert result == ""

def test_listen_with_whisper_transcribe_exception(monkeypatch, tmp_path):
    """
    Test listen_with_whisper returns empty string if transcription raises an exception.
    """
    mock_model = mock.MagicMock()
    mock_model.transcribe.side_effect = Exception("fail")
    monkeypatch.setattr(voice_input.whisper, "load_model", lambda name: mock_model)
    monkeypatch.setattr(voice_input.sd, "rec", lambda *a,
                        **k: mock_audio(duration=a[0]/k['samplerate'], samplerate=k['samplerate']))
    monkeypatch.setattr(voice_input.sd, "wait", lambda: None)
    monkeypatch.setattr(voice_input.os, "remove", lambda path: None)
    orig_wave_open = wave.open
    def fake_wave_open(path, mode):
        return orig_wave_open(str(tmp_path / "temp_audio.wav"), mode)
    monkeypatch.setattr(voice_input.wave, "open", fake_wave_open)
    result = voice_input.listen_with_whisper(duration=0.01)
    assert result == ""

def test_listen_with_whisper_remove_exception(monkeypatch, tmp_path):
    """
    Test listen_with_whisper returns empty string if transcription raises an exception.
    """
    mock_model = mock.MagicMock()
    mock_model.transcribe.return_value = {"text": "hi"}
    monkeypatch.setattr(voice_input.whisper, "load_model", lambda name: mock_model)
    monkeypatch.setattr(voice_input.sd, "rec", lambda *a,
                        **k: mock_audio(duration=a[0]/k['samplerate'], samplerate=k['samplerate']))
    monkeypatch.setattr(voice_input.sd, "wait", lambda: None)
    def raise_remove(path):
        raise OSError("fail remove")
    monkeypatch.setattr(voice_input.os, "remove", raise_remove)
    orig_wave_open = wave.open
    def fake_wave_open(path, mode):
        return orig_wave_open(str(tmp_path / "temp_audio.wav"), mode)
    monkeypatch.setattr(voice_input.wave, "open", fake_wave_open)
    result = voice_input.listen_with_whisper(duration=0.01)
    assert result == "hi"
