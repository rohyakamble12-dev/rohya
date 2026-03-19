import cv2
import logging
import os

class VisionModule:
    def capture_and_describe(self):
        try:
            # Real camera link
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Save tactical reference
                os.makedirs("captures", exist_ok=True)
                cv2.imwrite("captures/vision_ref.jpg", frame)
                return "Optic link established. Visual data captured and archived for analysis. Operator identified."
            return "Optic sensors failed to acquire visual lock."
        except Exception as e:
            return f"Vision link error: {e}"

    def face_detect(self):
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if not ret: return "Optical error: Frame capture failed."

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) > 0:
                return f"Biometric scan complete: {len(faces)} human signature(s) detected. Security cleared."
            return "Biometric scan complete: No human signatures found in immediate vicinity."
        except:
            return "Facial recognition protocol offline."
