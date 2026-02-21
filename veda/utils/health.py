import importlib
import requests
import os
import logging

# Setup logging
logging.basicConfig(filename='veda.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class VedaHealth:
    @staticmethod
    def check_dependencies():
        """Checks if required libraries are installed."""
        required = [
            'ollama', 'edge_tts', 'pyttsx3', 'speech_recognition',
            'customtkinter', 'pyautogui', 'pycaw', 'screen_brightness_control',
            'requests', 'bs4', 'wikipedia', 'PyPDF2', 'psutil', 'pynput', 'PIL', 'Crypto', 'pytesseract'
        ]
        missing = []
        for lib in required:
            try:
                importlib.import_module(lib)
            except ImportError:
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

        missing_deps = VedaHealth.check_dependencies()
        if missing_deps:
            report.append(f"Missing libraries: {', '.join(missing_deps)}")

        ollama_ok, ollama_msg = VedaHealth.check_ollama()
        if not ollama_ok:
            report.append(ollama_msg)

        audio_ok, audio_msg = VedaHealth.check_audio()
        if not audio_ok:
            report.append(audio_msg)

        return report

    @staticmethod
    def check_audio():
        """Checks if audio output is working."""
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return True, "Audio hardware detected."
        except Exception as e:
            return False, f"Audio hardware issue: {e}"
