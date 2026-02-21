import pyautogui
import pygetwindow as gw
from PIL import Image
import os
import cv2
import pytesseract

class VedaVision:
    def __init__(self, assistant_ref=None):
        self.assistant = assistant_ref
        # Note: In a real Windows environment, the user might need to set the path:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def _extract_text(self, image):
        """Helper to run OCR on an image."""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            return f"OCR Error: {str(e)}. Please ensure Tesseract-OCR is installed on your system."

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

    def analyze_current_view(self):
        """Summarizes what the user is currently looking at, including screen text."""
        info = self.get_active_window_info()
        if info:
            # Capture and read screen text
            screenshot = pyautogui.screenshot()
            text = self._extract_text(screenshot)

            summary = f"Digital Perception: You are active in '{info['title']}'."
            if text and len(text) > 10:
                # Use LLM to summarize if possible
                if self.assistant:
                    intel = self.assistant.llm.chat(f"I've read this text from the user's screen: '{text[:2000]}'. Briefly explain what they are looking at.")
                    return f"{summary}\nContent Intel: {intel}"
                return f"{summary}\nText detected: {text[:200]}..."
            return summary
        return "I can't see any active windows right now."

    def read_screen(self):
        """High-resolution OCR scan of the primary display."""
        screenshot = pyautogui.screenshot()
        text = self._extract_text(screenshot)
        if not text or len(text) < 5:
            return "Visual scan complete. I couldn't identify any readable text on the display."

        if self.assistant:
            return self.assistant.llm.chat(f"The following text was captured from the user's screen. Please analyze and summarize it for them: \n\n{text[:3000]}")
        return f"Captured text: {text[:500]}..."

    def read_physical_document(self, frame=None):
        """Uses the webcam to read text from a physical object."""
        try:
            if frame is None:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    return "Optical sensor failure: Unable to capture frame from webcam."

            # Convert OpenCV frame (BGR) to PIL Image (RGB) for OCR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)

            text = self._extract_text(pil_img)
            if not text or len(text) < 5:
                return "I can see the object, but I'm unable to resolve any legible text. Try adjusting the lighting or proximity."

            if self.assistant:
                return self.assistant.llm.chat(f"I am reading a physical document via webcam. Here is the raw OCR data: '{text[:2000]}'. Please provide a clean summary of what is written.")
            return f"I've read the following: {text[:500]}"
        except Exception as e:
            return f"Physical OCR failed: {str(e)}"

    @staticmethod
    def veda_sight(frame=None):
        """Captures a frame from the webcam and detects objects/faces."""
        try:
            if frame is None:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    return "I'm unable to access the optical sensor (webcam)."

            # Save for analysis
            cv2.imwrite("veda_sight.jpg", frame)

            # Simple Face Detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Multi-Sensor cascades
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
            upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

            eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
            bodies = body_cascade.detectMultiScale(gray, 1.1, 4)
            u_bodies = upper_body_cascade.detectMultiScale(gray, 1.1, 4)

            findings = []
            if len(faces) > 0: findings.append(f"{len(faces)} face(s)")
            if len(eyes) > 0: findings.append(f"{len(eyes)} retinal points")
            if len(bodies) > 0 or len(u_bodies) > 0: findings.append("biological entity detected")

            if findings:
                return f"Stark-Sensor Analysis: {', '.join(findings)}. Environment is secure."
            return "Visual scan complete. Area is clear. No unauthorized bio-signs detected."
        except Exception as e:
            return f"Sight error: {str(e)}"
