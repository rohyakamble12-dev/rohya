import os
import sys

def test_imports():
    print("--- REAL-WORLD MODULE IMPORT TEST ---")
    sys.path.append(os.getcwd())

    modules = [
        "modules.brain", "modules.ui", "modules.system", "modules.voice",
        "modules.commands", "modules.memory", "modules.notifications",
        "modules.monitor", "modules.intel", "modules.media", "modules.productivity",
        "modules.vision", "modules.files", "modules.protocols", "modules.iot",
        "modules.comms", "modules.automation"
    ]

    for mod in modules:
        try:
            __import__(mod)
            print(f"[OK] {mod}")
        except Exception as e:
            print(f"[FAIL] {mod}: {e}")

if __name__ == "__main__":
    test_imports()
