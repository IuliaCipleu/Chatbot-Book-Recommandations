"""Voice input utilities for speech recognition using Google and Whisper APIs."""

import os
import tempfile
import scipy.io.wavfile
import sounddevice as sd
import speech_recognition as sr
import whisper
import numpy as np
import torchaudio
import torch

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
    print("Listening for speech...")

    print(f"(Recording {duration} seconds...)")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()

    audio = audio.flatten()
    audio = np.int16(audio * 32767)  # Convert to 16-bit PCM

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        scipy.io.wavfile.write(temp_audio.name, sample_rate, audio)
        print("Audio saved, transcribing...")
        result = model.transcribe(temp_audio.name, language=language)
        os.unlink(temp_audio.name)
        return result["text"]
