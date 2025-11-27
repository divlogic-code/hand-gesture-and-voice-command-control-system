import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# --- Smooth movement buffer ---
def smooth_position(x, y, buffer, max_len=6):
    buffer.append((x, y))
    if len(buffer) > max_len:
        buffer.popleft()
    avg_x = int(np.mean([pos[0] for pos in buffer]))
    avg_y = int(np.mean([pos[1] for pos in buffer]))
    return avg_x, avg_y

# --- Finger Count ---
def count_fingers(landmarks):
    count = 0
    finger_tips = [8, 12, 16, 20]
    for tip in finger_tips:
        if landmarks[tip].y < landmarks[tip - 2].y:
            count += 1
    if landmarks[4].x < landmarks[3].x:
        count += 1
    return count

# --- Special Gestures ---
def detect_special_gesture(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    wrist = landmarks[0]

    # Fist
    if all(abs(l.y - wrist.y) < 0.12 for l in [thumb_tip, index_tip]):
        return "fist"

    # Pinch
    dist = np.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
    if dist < 0.05:
        return "pinch"

    return None

# --- Click Cooldown ---
last_action_time = 0
cooldown = 0.9
def can_trigger():
    global last_action_time
    if time.time() - last_action_time > cooldown:
        last_action_time = time.time()
        return True
    return False

# --- MAIN Gesture Control ---
def run_gesture_control():
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1)
    screen_w, screen_h = pyautogui.size()
    pos_buffer = deque()

    print("🖐 Gesture Control Running... (Press 'q' to stop)")
    action_text = ""

    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                finger_count = count_fingers(landmarks)
                special = detect_special_gesture(landmarks)

                index = landmarks[8]
                cam_w, cam_h = cap.get(3), cap.get(4)

                x = int(index.x * cam_w)
                y = int(index.y * cam_h)

                cursor_x = np.interp(x, [0, cam_w], [0, screen_w])
                cursor_y = np.interp(y, [0, cam_h], [0, screen_h])

                cursor_x, cursor_y = smooth_position(cursor_x, cursor_y, pos_buffer)

                # --- Special Gestures: FIST + PINCH ---
                if special and can_trigger():
                    if special == "pinch":
                        pyautogui.hotkey("win", "down")
                        action_text = "🤏 Minimize Window"
                    elif special == "fist":
                        pyautogui.press("f5")
                        action_text = "▶ Start Slideshow"
                    continue

                # --- 1 Finger: Move Cursor ---
                if finger_count == 1:
                    pyautogui.moveTo(cursor_x, cursor_y, duration=0.01)
                    action_text = "🖱 Cursor Move"

                # --- 2 Fingers: Smooth Fast Scroll ---
                elif finger_count == 2:
                    scroll_speed = 70
                    if y < cam_h / 2:
                        pyautogui.scroll(scroll_speed)
                        action_text = "📜 Scrolling Up"
                    else:
                        pyautogui.scroll(-scroll_speed)
                        action_text = "📜 Scrolling Down"

                # --- 3 Fingers: Next Slide ---
                elif finger_count == 3 and can_trigger():
                    pyautogui.press("right")
                    action_text = "➡ Next Slide"

                # --- 4 Fingers: Previous Slide ---
                elif finger_count == 4 and can_trigger():
                    pyautogui.press("left")
                    action_text = "⬅ Previous Slide"

                # --- 5 Fingers: Click ---
                elif finger_count == 5 and can_trigger():
                    pyautogui.click()
                    action_text = "🖐 Left Click"

        cv2.putText(frame, f"Action: {action_text}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        cv2.imshow("Gesture Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_gesture_control()
