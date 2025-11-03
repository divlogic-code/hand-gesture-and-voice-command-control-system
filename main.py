import threading
from gesture_control import start_gesture_control
from voice_control import start_voice_control

if __name__ == "__main__":
    print("Starting Laptop Control AI System...")
    t1 = threading.Thread(target=start_gesture_control)
    t2 = threading.Thread(target=start_voice_control)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
