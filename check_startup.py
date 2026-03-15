from unittest.mock import MagicMock, patch
import sys

# Mock modules
sys.modules['ollama'] = MagicMock()
sys.modules['pyttsx3'] = MagicMock()
sys.modules['edge_tts'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['pycaw'] = MagicMock()
sys.modules['pycaw.pycaw'] = MagicMock()
sys.modules['comtypes'] = MagicMock()
sys.modules['screen_brightness_control'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['pygetwindow'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['wikipedia'] = MagicMock()
sys.modules['PyPDF2'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['schedule'] = MagicMock()
sys.modules['vosk'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()

try:
    from veda.core.assistant import VedaAssistant
    gui = MagicMock()
    # Mock left panel for plan updates
    gui.left = MagicMock()
    with patch('veda.core.memory.sqlite3.connect'), \
         patch('veda.features.tasks.sqlite3.connect'), \
         patch('veda.features.calendar.sqlite3.connect'):
        assistant = VedaAssistant(gui)
        print("[SUCCESS]: Veda Core HUD v4.0 (Friday Edition) ready.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"[ERROR]: {e}")
    sys.exit(1)
