import sys
import os
from unittest.mock import MagicMock, patch

# Mock everything
modules_to_mock = [
    'customtkinter', 'edge_tts', 'pyttsx3', 'speech_recognition',
    'pygame', 'ollama', 'psutil', 'pyautogui', 'ctypes', 'cv2',
    'win10toast', 'pynput', 'pynput.keyboard', 'PyPDF2', 'wikipedia',
    'deep_translator', 'comtypes', 'screen_brightness_control', 'pycaw.pycaw',
    'schedule', 'winshell', 'pytesseract', 'numpy', 'mediapipe'
]

for mod in modules_to_mock:
    mock = MagicMock()
    if mod == 'numpy': mock.__version__ = "2.0.0"
    sys.modules[mod] = mock

def diagnostic():
    print("--- VEDA SOVEREIGN STARTUP DIAGNOSTIC ---")
    try:
        # Add current dir to path
        sys.path.append(os.getcwd())

        from main import VedaAssistant
        print("[OK] main.py - VedaAssistant class found.")

        # Test instantiation
        with patch('main.VedaHUD'), patch('main.VedaVoice'), patch('main.VedaBrain'), \
             patch('main.CommandRouter'), patch('main.VedaMemory'), patch('main.NotificationModule'):
            assistant = VedaAssistant()
            print("[OK] Assistant Kernel Instantiation.")

        print("[SUCCESS] Veda Sovereign Architecture Verified.")
        return True
    except Exception as e:
        print(f"[CRITICAL FAIL]: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if diagnostic():
        sys.exit(0)
    else:
        sys.exit(1)
