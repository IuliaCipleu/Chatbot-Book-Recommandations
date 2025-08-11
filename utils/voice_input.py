import speech_recognition as sr

def listen_to_microphone(language="en-US"):
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
