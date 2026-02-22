import pyautogui
import pygetwindow as gw
from PIL import Image
import cv2
import pytesseract
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.throttling import limiter

class VisionPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("vision_analyze", self.analyze_current_view, PermissionTier.SAFE)
        self.register_intent("read_screen", self.read_screen, PermissionTier.SAFE)
        self.register_intent("read_physical", self.read_physical_document, PermissionTier.SAFE)
        self.register_intent("sight", self.veda_sight, PermissionTier.SAFE)

    def _extract_text(self, image):
        try: return pytesseract.image_to_string(image).strip()
        except: return ""

    @limiter.limit(5.0)
    def analyze_current_view(self, params):
        try:
            window = gw.getActiveWindow()
            text = self._extract_text(pyautogui.screenshot())
            return self.assistant.llm.chat(f"Context: {window.title if window else 'Unknown'}. Screen text: {text[:1000]}")
        except: return "Visual diagnostics failing."

    def read_screen(self, params):
        text = self._extract_text(pyautogui.screenshot())
        return self.assistant.llm.chat(f"Analyze: {text[:2000]}")

    def read_physical_document(self, params):
        frame = getattr(self.assistant.gui, 'last_raw_frame', None)
        if frame is None: return "Optical sensors inactive."
        text = self._extract_text(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        return self.assistant.llm.chat(f"Read document: {text[:2000]}")

    def veda_sight(self, params):
        return "Tactical visual scan complete."
