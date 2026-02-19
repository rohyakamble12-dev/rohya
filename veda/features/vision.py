import pyautogui
import pygetwindow as gw
from PIL import Image
import os

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
            if window:
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
