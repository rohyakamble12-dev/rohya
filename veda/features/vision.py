import pyautogui
import pygetwindow as gw
from PIL import Image
import cv2
import pytesseract
from veda.features.base import VedaPlugin, PermissionTier

class VisionPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("vision_analyze", self.analyze_current_view, PermissionTier.SAFE)
        self.register_intent("read_screen", self.read_screen, PermissionTier.SAFE)
        self.register_intent("read_physical", self.read_physical_document, PermissionTier.SAFE)
        self.register_intent("sight", self.veda_sight, PermissionTier.SAFE)

    def _extract_text(self, image):
        try:
            return pytesseract.image_to_string(image).strip()
        except Exception as e:
            return f"OCR Failure: {e}"

    def analyze_current_view(self, params):
        try:
            window = gw.getActiveWindow()
            title = window.title if window else "Unknown"
            screenshot = pyautogui.screenshot()
            text = self._extract_text(screenshot)

            prompt = f"I am looking at a window titled '{title}'. The screen contains: '{text[:1500]}'. Summarize my context."
            return self.assistant.llm.chat(prompt)
        except Exception as e:
            return f"Analysis failed: {e}"

    def read_screen(self, params):
        screenshot = pyautogui.screenshot()
        text = self._extract_text(screenshot)
        if not text: return "No legible text found on display."
        return self.assistant.llm.chat(f"Analyze this screen capture: {text[:2500]}")

    def read_physical_document(self, params):
        frame = getattr(self.assistant.gui, 'last_raw_frame', None)
        if frame is None:
            return "Optical sensors are offline. Please enable the camera."

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)
        text = self._extract_text(pil_img)
        if not text: return "I can see the object, but the text is unreadable."
        return self.assistant.llm.chat(f"Summarize this document I am holding: {text[:2000]}")

    def veda_sight(self, params):
        frame = getattr(self.assistant.gui, 'last_raw_frame', None)
        if frame is None: return "Sensors offline."

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            return f"Biometric alert: {len(faces)} human signature(s) detected. Security nominal."
        return "Area clear. No active bio-signals detected."
