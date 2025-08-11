"""Voice input utilities for speech recognition using Google and Whisper APIs."""

import os
import tempfile
import wave
import sounddevice as sd
import speech_recognition as sr
import whisper
import numpy as np
    # removed unused imports



def listen_to_microphone(language="en-US"):
    """
    Listens to the microphone and converts spoken words to text using Google's Speech
    Recognition API.
    Args:
        language (str): The language code for speech recognition (default is "en-US").
    Returns:
        str: The recognized text from the audio input. Returns an empty string if the audio could not be understood or if there was a recognition error.
    Raises:
        None: All exceptions are handled within the function.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Listening... (speak clearly, press Ctrl+C to stop)")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=language)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError as e:
        print(f"Speech Recognition error: {e}")
    return ""

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

    # Save to a temporary file using the built-in wave module for compatibility
    fd, temp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with wave.open(temp_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    try:
        print("📥 Audio saved, transcribing...")
        result = model.transcribe(temp_path, language=language)
        print(f"🗣️ Transcribed: {result['text']}")
        return result["text"]
    except Exception as e:
        print(f"❌ Whisper failed: {e}")
        return ""
    finally:
        try:
            os.remove(temp_path)
        except Exception as cleanup_err:
            print(f"⚠️ Could not delete temp file: {cleanup_err}")
            