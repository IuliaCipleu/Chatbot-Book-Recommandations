"""Voice input utilities for speech recognition using Whisper APIs."""

import os
import wave
import sounddevice as sd
import whisper
import numpy as np


def listen_with_whisper(duration=5, sample_rate=16000, language="en"):
    """
    Records audio from the microphone for a specified duration, transcribes the speech using OpenAI's Whisper model, and returns the recognized text.
    Args:
        duration (int, optional): Duration of the audio recording in seconds. Defaults to 5.
        sample_rate (int, optional): Sampling rate for the audio recording. Defaults to 16000.
        language (str, optional): Language code for transcription (e.g., "en" for English). Defaults to "en".
    Returns:
        str: The transcribed text from the recorded audio.
    """
    model = whisper.load_model("base")
    print("🎤 Listening for speech...")
    print(f"(Recording {duration} seconds...)")

    # Record from mic
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()

    # Convert to 16-bit PCM
    audio = (audio * 32767).astype(np.int16).flatten()

    # Save to a fixed file in the current directory for Windows compatibility
    temp_path = "temp_audio.wav"
    with wave.open(temp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    try:
        print(f"📥 Audio saved at: {os.path.abspath(temp_path)}, transcribing...")
        print(f"[DEBUG] File exists before transcription: {os.path.exists(temp_path)}")
        if not os.path.exists(temp_path):
            print(f"❌ Temp file does not exist: {temp_path}, creating empty WAV file.")
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(b'')
        # Double-check file is closed and accessible
        try:
            with open(temp_path, 'rb') as f:
                f.read(1)
        except Exception as file_err:
            print(f"[DEBUG] Could not open file before transcription: {file_err}")
        result = model.transcribe(temp_path, language=language)
        if isinstance(result, dict) and 'text' in result:
            print(f"🗣️ Transcribed: {result['text']}")
            return result["text"]
        else:
            print(f"❌ Whisper returned error: {result}")
            return ""
    except Exception as e:
        print(f"❌ Whisper failed: {e}")
        return ""
    finally:
        try:
            os.remove(temp_path)
        except Exception as cleanup_err:
            print(f"⚠️ Could not delete temp file: {cleanup_err}")
