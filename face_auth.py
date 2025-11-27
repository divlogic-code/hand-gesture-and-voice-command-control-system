import cv2
import face_recognition
import time
import sys

# --- Configuration ---
KNOWN_FACE_PATH = "known_faces/owner.jpg"
TOLERANCE = 0.45         # Lower = stricter match
CHECK_INTERVAL = 1.8     # Seconds between recognition checks
CAM_INDEX = 0            # 0 = Default Camera

def authenticate_user():
    print("🔒 Scanning for authorized user...")

    # --- Load and convert known face safely ---
    known_image = cv2.imread(KNOWN_FACE_PATH)

    if known_image is None:
        print(f"❌ ERROR: Could not load image — {KNOWN_FACE_PATH}")
        print("➡ Make sure the image is .jpg/.png and inside known_faces folder.")
        return False

    # Force correct format (fixes 'Unsupported image type' error)
    try:
        known_image = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB).astype("uint8")
    except:
        print("❌ ERROR: Unable to convert 'owner.jpg' to valid RGB format.")
        return False

    known_encodings = face_recognition.face_encodings(known_image)
    if not known_encodings:
        print("❌ ERROR: No face detected in 'owner.jpg'. Use a clear front-face photo.")
        return False

    known_encoding = known_encodings[0]

    # --- Start webcam ---
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print("❌ ERROR: Webcam not detected.")
        return False

    last_check = time.time()
    print("📸 Please look at the camera to verify identity...")
    print("👉 Press 'Q' anytime to cancel authentication.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # Run recognition periodically
        if time.time() - last_check > CHECK_INTERVAL:
            last_check = time.time()
            face_locations = face_recognition.face_locations(rgb_small)
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            for encoding in face_encodings:
                match = face_recognition.compare_faces(
                    [known_encoding], encoding, tolerance=TOLERANCE
                )[0]

                if match:
                    print("\n✅ Authorized user recognized!")
                    print("🔓 Access Granted.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

        # Show display window
        cv2.putText(frame, "Authenticating...", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Face Authentication - Press Q to cancel", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("❌ Authentication cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return False


if __name__ == "__main__":
    authenticate_user()
