import threading
from gesture_control import run_gesture_control
from voice_control import run_voice_control
from face_auth import authenticate_user  # 🧠 Import face recognition

if __name__ == "__main__":
    print("🧠 LaptopControlAI - Smart Assistant with Gesture + Voice + Face Recognition")
    print("--------------------------------------------------------------")

    # Step 1: Authenticate the user before running anything
    if authenticate_user():
        print("✅ Access Granted! Starting Gesture and Voice Control...\n")

        # Step 2: Run both controls in parallel threads
        gesture_thread = threading.Thread(target=run_gesture_control)
        voice_thread = threading.Thread(target=run_voice_control)

        gesture_thread.start()
        voice_thread.start()

        gesture_thread.join()
        voice_thread.join()

        print("🛑 Both Gesture and Voice controls have stopped.")
    else:
        print("🚫 Unauthorized User. Access Denied.")
