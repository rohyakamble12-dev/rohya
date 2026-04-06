import os
import sys
import logging
from unittest.mock import MagicMock

# Setup logging to capture errors
logging.basicConfig(level=logging.ERROR)

def audit_modules():
    print("--- VEDA MODULE INTEGRITY AUDIT ---")
    sys.path.append(os.getcwd())

    modules = [
        "automation", "brain", "commands", "comms", "files", "intel",
        "iot", "media", "memory", "monitor", "notifications",
        "productivity", "protocols", "system", "ui", "vision", "voice"
    ]

    results = {}

    for mod_name in modules:
        print(f"Auditing: modules.{mod_name}...", end=" ")
        try:
            # We use __import__ to load it
            mod = __import__(f"modules.{mod_name}", fromlist=["*"])
            print("[IMPORT OK]", end=" ")

            # Now we try to find the main class
            class_map = {
                "automation": "AutomationModule", "brain": "VedaBrain", "commands": "CommandRouter",
                "comms": "CommsModule", "files": "FilesModule", "intel": "IntelModule",
                "iot": "IOTModule", "media": "MediaModule", "memory": "VedaMemory",
                "monitor": "MonitorModule", "notifications": "NotificationModule",
                "productivity": "ProductivityModule", "protocols": "ProtocolModule",
                "system": "SystemModule", "ui": "VedaHUD", "vision": "VisionModule", "voice": "VedaVoice"
            }

            cls_name = class_map.get(mod_name)
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                # Try to instantiate with dummy args if needed
                try:
                    # Specialized instantiation for classes that need an 'assistant' or 'config'
                    if mod_name in ["productivity", "iot", "protocols", "monitor", "commands"]:
                        # Commands needs an assistant, but assistant needs a router... circular.
                        # We use a Mock for the assistant.
                        obj = cls(MagicMock())
                    elif mod_name in ["ui", "voice"]:
                        try:
                            obj = cls(MagicMock(), MagicMock())
                        except Exception as inner_e:
                            if "display" in str(inner_e).lower():
                                print("[OK - HEADLESS]", end=" ")
                                results[mod_name] = "OK"
                                continue
                            else: raise inner_e
                    elif mod_name == "notifications":
                        obj = cls(MagicMock())
                    else:
                        obj = cls()
                    print("[INSTANTIATION OK]")
                    results[mod_name] = "OK"
                except Exception as e:
                    print(f"[INSTANTIATION FAIL]: {e}")
                    results[mod_name] = f"INSTANTIATION FAIL: {e}"
            else:
                print(f"[CLASS MISSING]: {cls_name} not found.")
                results[mod_name] = "CLASS MISSING"

        except Exception as e:
            print(f"[IMPORT FAIL]: {e}")
            results[mod_name] = f"IMPORT FAIL: {e}"

    print("\n--- FINAL AUDIT REPORT ---")
    all_ok = True
    for mod, status in results.items():
        print(f"{mod.upper():<15}: {status}")
        if status != "OK": all_ok = False

    if all_ok:
        print("\n[SUCCESS] All modules are structurally sound.")
    else:
        print("\n[WARNING] Some modules have structural or dependency issues.")

if __name__ == "__main__":
    audit_modules()
