import cv2
import mediapipe as mp
import pyautogui

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Example custom gestures
def detect_gesture(landmarks):
    # You can customize these rules
    thumb_tip = landmarks[4].y
    index_tip = landmarks[8].y
    middle_tip = landmarks[12].y

    # Example gestures
    if index_tip < thumb_tip and middle_tip > index_tip:
        return "move_up"
    elif index_tip > thumb_tip and middle_tip < thumb_tip:
        return "move_down"
    elif index_tip < thumb_tip and middle_tip < thumb_tip:
        return "click"
    else:
        return None


def start_gesture_control():
    cap = cv2.VideoCapture(0)
    hands = mp_hands.Hands(max_num_hands=1)
    screen_width, screen_height = pyautogui.size()

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                gesture = detect_gesture(hand_landmarks.landmark)
                if gesture == "move_up":
                    pyautogui.moveRel(0, -30)
                elif gesture == "move_down":
                    pyautogui.moveRel(0, 30)
                elif gesture == "click":
                    pyautogui.click()

                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
