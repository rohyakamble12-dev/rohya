import sys
import os
import subprocess
import ctypes

def show_error(title, message):
    """Shows a native Windows message box."""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)
    except:
        print(f"\n[CRITICAL ERROR]: {title}\n{message}")

def pre_flight_check():
    """Verifies critical modules before attempting to load the UI."""
    required = ["customtkinter", "PIL", "psutil", "cv2"]
    missing = []

    for module in required:
        try:
            __import__(module if module != "cv2" else "cv2")
        except ImportError:
            missing.append(module)

    if missing:
        msg = f"Critical Tactical Links Missing: {', '.join(missing)}\n\nPlease run 'python install_deps.py' or 'repair_veda.bat' to re-establish connections."
        show_error("VEDA CORE - LINK FAILURE", msg)
        return False
    return True

def main():
    if not pre_flight_check():
        sys.exit(1)

    try:
        # Import core only after flight check
        from veda.ui.gui import VedaGUI
        from veda.core.assistant import VedaAssistant

        class VedaController:
            def __init__(self):
                self.gui = VedaGUI(on_send_callback=self.on_send, on_voice_callback=self.on_voice)
                self.assistant = VedaAssistant(self.gui)
                print(f"[SYSTEM]: Intelligence Linked.")

            def on_send(self, message):
                return self.assistant.process_command(message)

            def on_voice(self):
                self.assistant.listen_and_process()

            def run(self):
        self.gui.run_boot_sequence()
                self.gui.mainloop()

        controller = VedaController()
        controller.run()

    except Exception as e:
        show_error("VEDA CORE - KERNEL PANIC", f"An unexpected error collapsed the neural link:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
