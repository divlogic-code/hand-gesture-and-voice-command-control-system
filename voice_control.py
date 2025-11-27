import os
import queue
import sounddevice as sd
import pyautogui
import json
import difflib
from vosk import Model, KaldiRecognizer
import subprocess  # for opening apps

def run_voice_control():
    model_path = "vosk_model"
    if not os.path.exists(model_path):
        print("❌ Vosk model not found! Download and extract as 'vosk_model' in your folder.")
        return

    print("🎤 Voice Control Running (Offline)... Say 'stop' to quit.")

    model = Model(model_path)
    rec = KaldiRecognizer(model, 16000)
    q = queue.Queue()

    # 🎯 Define command mapping
    commands = {
        "click": lambda: pyautogui.click(),
        "scroll up": lambda: pyautogui.scroll(200),
        "scroll down": lambda: pyautogui.scroll(-200),
        "move up": lambda: pyautogui.moveRel(0, -50),
        "move down": lambda: pyautogui.moveRel(0, 50),
        "move left": lambda: pyautogui.moveRel(-50, 0),
        "move right": lambda: pyautogui.moveRel(50, 0),
        "volume up": lambda: pyautogui.press("volumeup"),
        "volume down": lambda: pyautogui.press("volumedown"),
        "mute": lambda: pyautogui.press("volumemute"),
        "unmute": lambda: pyautogui.press("volumemute"),
        "next slide": lambda: pyautogui.press("right"),
        "previous slide": lambda: pyautogui.press("left"),
        "start slideshow": lambda: pyautogui.press("f5"),
        "exit slideshow": lambda: pyautogui.press("esc"),
        "switch window": lambda: pyautogui.hotkey("alt", "tab"),
        "close window": lambda: pyautogui.hotkey("alt", "f4")
    }

    # -------------------------------
    # 💻 Define apps to open
    # -------------------------------
    APP_PATHS = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "pinterest": r"C:\Users\divkr\AppData\Local\Programs\Pinterest\Pinterest.exe",
        "vs code": r"C:\Users\divkr\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "notepad": "notepad",
        "calculator": "calc"
    }

    def find_best_match(cmd_text):
        return difflib.get_close_matches(cmd_text, commands.keys(), n=1, cutoff=0.6)

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    print("🎧 Listening on device:", sd.query_devices(1)['name'])
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, device=1, callback=callback):
        print("✅ Microphone detected, initializing model...")

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'text' in result:
                    cmd = result['text'].strip().lower()
                    if not cmd:
                        continue

                    print(f"🗣 You said: {cmd}")

                    if "stop" in cmd:
                        print("🛑 Voice Control Stopped.")
                        break

                    # 🔹 Check if user wants to open an app
                    if cmd.startswith("open "):
                        app_name = cmd.replace("open ", "").strip()
                        if app_name in APP_PATHS:
                            try:
                                os.startfile(APP_PATHS[app_name])
                                print(f"🚀 Opening {app_name}")
                            except Exception as e:
                                print(f"⚠️ Failed to open {app_name}: {e}")
                        else:
                            print(f"❌ App '{app_name}' not in APP_PATHS")
                        continue

                    # 🔍 Try exact or close match for existing commands
                    matched = find_best_match(cmd)
                    if matched:
                        print(f"✅ Command recognized: {matched[0]}")
                        try:
                            commands[matched[0]]()
                        except Exception as e:
                            print(f"⚠️ Error executing command: {e}")
                    else:
                        print("❌ Unrecognized command.")
