import os
try:
    if os.environ.get('DISPLAY'):
        import pyautogui
    else:
        pyautogui = None
except (ImportError, KeyError):
    pyautogui = None
try:
    import pygetwindow as gw
except (ImportError, NotImplementedError):
    gw = None
from PIL import Image
try:
    import cv2
except ImportError:
    cv2 = None
try:
    import pytesseract
except ImportError:
    pytesseract = None
from veda.features.base import VedaPlugin, PermissionTier
from veda.utils.throttling import limiter

class VisionPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("vision_analyze", self.analyze_current_view, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("read_screen", self.read_screen, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("read_physical", self.read_physical_document, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("sight", self.veda_sight, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})

    def _extract_text(self, image):
        if not pytesseract: return ""
        try: return pytesseract.image_to_string(image).strip()
        except Exception as e: return ""

    @limiter.limit(5.0)
    def analyze_current_view(self, params):
        if not pyautogui: return "Screen capture restricted."
        try:
            window = gw.getActiveWindow() if gw else None
            text = self._extract_text(pyautogui.screenshot())
            return self.assistant.llm.chat(f"Context: {window.title if window else 'Unknown'}. Screen text: {text[:1000]}")
        except Exception as e: return "Visual diagnostics failing."

    def read_screen(self, params):
        if not pyautogui: return "Screen capture restricted."
        text = self._extract_text(pyautogui.screenshot())
        return self.assistant.llm.chat(f"Analyze: {text[:2000]}")

    def read_physical_document(self, params):
        if not cv2: return "Optical sensors restricted (OpenCV missing)."
        frame = getattr(self.assistant.gui, 'last_raw_frame', None)
        if frame is None: return "Optical sensors inactive."
        text = self._extract_text(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        return self.assistant.llm.chat(f"Read document: {text[:2000]}")

    def veda_sight(self, params):
        """Webcam Snapshot Analysis."""
        if not cv2: return "Optical sensors offline (OpenCV missing)."
        import os
        frame = getattr(self.assistant.gui, 'last_raw_frame', None)
        if frame is None: return "Optical sensors offline."

        # Save tactical snapshot
        save_path = os.path.join(os.path.expanduser("~"), "Pictures", "Veda_Sight.jpg")
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, frame)
            return f"Tactical snapshot secured at {save_path}."
        except Exception as e:
            return f"Snapshot capture failed: {e}"
