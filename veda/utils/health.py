import importlib
import requests
import os
from veda.utils.logger import logger

class VedaHealth:
    @staticmethod
    def check_dependencies():
        """Checks if required libraries are installed with platform-aware safety."""
        required = [
            'ollama', 'edge_tts', 'pyttsx3', 'speech_recognition',
            'customtkinter', 'pyautogui', 'pycaw', 'screen_brightness_control',
            'requests', 'bs4', 'wikipedia', 'PyPDF2', 'psutil', 'pynput', 'PIL',
            'Crypto', 'pytesseract', 'keyboard', 'winshell'
        ]
        missing = []
        for lib in required:
            try:
                # Strategic Check: If library is known to require DISPLAY (like pyautogui/customtkinter),
                # only import if we are in a GUI environment.
                if lib in ['pyautogui', 'customtkinter', 'screen_brightness_control'] and not os.environ.get('DISPLAY') and os.name != 'nt':
                     continue

                importlib.import_module(lib)
            except (ImportError, KeyError, Exception):
                missing.append(lib)
        return missing

    @staticmethod
    def check_ollama(model="llama3.2:3b"):
        """Checks if Ollama is running and the model is pulled."""
        try:
            # Check connection
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                return False, "Ollama server returned an error."

            # Check for model
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            if model not in model_names and f"{model}:latest" not in model_names:
                return False, f"Model '{model}' not found. Please run 'ollama pull {model}'"

            return True, "Ollama is healthy."
        except Exception as e:
            return False, f"Could not connect to Ollama. Is it running? ({e})"

    @staticmethod
    def full_report():
        """Returns a list of warnings or errors."""
        report = []

        # Check DISPLAY environment for GUI/OpenCV dependencies
        if os.name != 'nt' and not os.environ.get('DISPLAY'):
             # We are likely in a headless environment, skip GUI-dependent health checks
             pass

        missing_deps = VedaHealth.check_dependencies()
        if missing_deps:
            report.append(f"Missing libraries: {', '.join(missing_deps)}")

        ollama_ok, ollama_msg = VedaHealth.check_ollama()
        if not ollama_ok:
            report.append(ollama_msg)

        audio_ok, audio_msg = VedaHealth.check_audio()
        if not audio_ok:
            report.append(audio_msg)

        # Sector Integrity
        try:
            from veda.core.registry import registry
            assistant = registry.get("assistant")
            if assistant and not assistant.plugins.intent_map:
                report.append("Tactical Matrix: Desync detected.")
        except Exception: pass

        return report

    @staticmethod
    def check_audio():
        """Checks if audio output is working."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                try:
                    pygame.mixer.init()
                except Exception:
                    return False, "Audio hardware restricted or in use."
            return True, "Audio hardware detected."
        except ImportError:
            return False, "Audio library (pygame) missing."
        except Exception as e:
            return False, f"Audio hardware issue: {e}"
