import speech_recognition as sr

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"Recognized: {text}")
        return text
    except Exception as e:
        print(f"Error: {e}")
        return ""
