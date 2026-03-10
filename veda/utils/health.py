import sys
import os
import importlib.util

def check_dependencies():
    """Checks for essential dependencies and reports status."""
    deps = {
        "ollama": "ollama",
        "pyttsx3": "pyttsx3",
        "speech_recognition": "speech_recognition",
        "pyautogui": "pyautogui",
        "pycaw": "pycaw.pycaw",
        "sbc": "screen_brightness_control",
        "requests": "requests",
        "duckduckgo_search": "duckduckgo_search"
    }

    missing = []
    for name, module in deps.items():
        if importlib.util.find_spec(module) is None:
            missing.append(name)

    return missing

def get_system_summary():
    import platform
    return {
        "os": platform.system(),
        "version": platform.version(),
        "python": sys.version.split()[0],
        "missing_deps": check_dependencies()
    }
