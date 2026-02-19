import pyautogui
import pygetwindow as gw
from PIL import Image
import os
import cv2

class VedaVision:
    @staticmethod
    def capture_screen():
        """Captures the current screen and returns the path."""
        path = "veda_vision_temp.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return path

    @staticmethod
    def get_active_window_info():
        """Returns info about the currently active window."""
        try:
            window = gw.getActiveWindow()
            if window and window.title:
                return {
                    "title": window.title,
                    "box": (window.left, window.top, window.width, window.height)
                }
            return None
        except:
            return None

    @staticmethod
    def analyze_current_view():
        """Summarizes what the user is currently looking at."""
        info = VedaVision.get_active_window_info()
        if info:
            return f"You are currently using '{info['title']}'."
        return "I can't see any active windows right now."

    @staticmethod
    def veda_sight():
        """Captures a frame from the webcam and detects objects/faces."""
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if not ret:
                return "I'm unable to access the optical sensor (webcam)."

            # Save for analysis
            cv2.imwrite("veda_sight.jpg", frame)

            # Simple Face Detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            cap.release()

            if len(faces) > 0:
                return f"Sensor analysis complete. I detected {len(faces)} person(s) in the vicinity."
            return "Visual scan complete. The immediate area appears to be clear."
        except Exception as e:
            return f"Sight error: {str(e)}"
