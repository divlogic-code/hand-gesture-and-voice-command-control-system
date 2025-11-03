import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import pyautogui

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def execute_command(command):
    command = command.lower()

    if "open chrome" in command:
        speak("Opening Google Chrome")
        os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")

    elif "increase volume" in command:
        for _ in range(5):
            pyautogui.press("volumeup")

    elif "decrease volume" in command:
        for _ in range(5):
            pyautogui.press("volumedown")

    elif "close window" in command:
        pyautogui.hotkey("alt", "f4")

    elif "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    else:
        speak("Sorry, I didn’t understand that command.")

def start_voice_control():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        speak("Voice control activated. Speak a command.")
        while True:
            print("Listening...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                execute_command(command)
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
            except sr.RequestError:
                speak("Speech service unavailable.")
