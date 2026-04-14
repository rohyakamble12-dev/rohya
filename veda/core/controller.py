import sys
import traceback
import threading
from veda.utils.logger import logger
from veda.ui.gui import VedaGUI
from veda.core.assistant import VedaAssistant
from veda.utils.threads import manager as thread_manager

class VedaController:
    """
    Central Controller for Veda AI-OS.
    Manages lifecycle, dependencies, and thread-safe interactions between UI and Core.
    """
    def __init__(self):
        self.gui = None
        self.assistant = None
        self.is_running = True
        self._setup_crash_handler()

    def _setup_crash_handler(self):
        sys.excepthook = self._global_exception_handler

    def _global_exception_handler(self, exctype, value, tb):
        """Fail-safe crash handler."""
        error_msg = "".join(traceback.format_exception(exctype, value, tb))
        try:
            logger.error(f"UNCAUGHT SYSTEM EXCEPTION: {error_msg}")
        except Exception as e:
            # Fallback to stderr if logger is compromised
            sys.stderr.write(f"CRITICAL LOGGER FAILURE. Crash log: {error_msg}\n")

        print(f"CRITICAL SYSTEM ERROR: {value}")
        # Attempt graceful emergency save
        if self.assistant:
            try: self.assistant.shutdown()
            except Exception as e: logger.warning(f"Tactical Silencing: {e}")

    def bootstrap(self):
        """Initializes the tactical matrix."""
        try:
            # 1. Initialize UI
            self.gui = VedaGUI(
                on_send_callback=self.handle_ui_input,
                on_voice_callback=self.handle_voice_trigger,
                on_upload_callback=self.handle_file_upload,
                on_closing_callback=self.shutdown
            )

            # 2. Initialize Assistant inside Controller
            self.assistant = VedaAssistant(self.gui)
            self.gui.assistant = self.assistant # Link for UI property access

            # 3. Bind protocol sync
            self.gui.protocol_callback = self.assistant.sync_protocols

            # 4. Start Background Listeners
            self._start_background_services()

            # 5. Register Hotkeys
            self._register_hotkeys()

            logger.info("Veda Controller: Bootstrap complete.")

            # Start GUI loop (blocking)
            self.gui.mainloop()

        except Exception as e:
            logger.error(f"Bootstrap Failure: {e}")
            sys.exit(1)

    def _start_background_services(self):
        """Initiates persistent background threads."""
        import time
        def wake_word_loop():
            while self.is_running:
                result = self.assistant.voice.listen_for_wake_word("veda")
                if result:
                    res_lower = result.lower()
                    if res_lower == "veda":
                        self.gui.after(0, self.gui.trigger_voice)
                    elif res_lower.startswith("veda"):
                        command = result[4:].strip()
                        if command:
                            self.gui.after(0, lambda: self.gui.update_chat("You", command))
                            # Process in background thread to avoid freezing UI
                            thread_manager.start_thread(f"VoiceCommand_{time.time()}",
                                                      self.assistant.process_command, args=(command,))
                # Small sleep to prevent tight loop if listener returns instantly
                time.sleep(0.1)

        thread_manager.start_thread("WakeWordService", wake_word_loop)

    def _register_hotkeys(self):
        try:
            import keyboard
            keyboard.add_hotkey('alt+v', lambda: self.gui.after(0, self.gui.trigger_voice))
            keyboard.add_hotkey('ctrl+alt+k', lambda: self.gui.after(0, self.shutdown))
        except Exception as e:
            logger.warning(f"Hotkeys Restricted: {e}")

    def handle_ui_input(self, text):
        """Thread-safe UI input handling."""
        # Ensure heavy processing doesn't block the UI thread
        thread_manager.start_thread(f"UICommand_{hash(text)}",
                                  self.assistant.process_command, args=(text,))

    def handle_voice_trigger(self):
        """Starts the voice recognition sequence."""
        thread_manager.start_thread("VoiceRecognition", self.assistant.listen_and_process)

    def handle_file_upload(self, paths):
        thread_manager.start_thread("FileUpload", self.assistant.process_file, args=(paths,))

    def shutdown(self):
        """Unified graceful shutdown sequence."""
        if not self.is_running: return
        self.is_running = False

        logger.info("Veda Controller: Initiating graceful shutdown.")

        try:
            if self.assistant:
                self.assistant.shutdown()

            if self.gui:
                self.gui.destroy()
        except Exception as e:
            logger.error(f"Shutdown Sequence Warning: {e}")
        finally:
            # Final cleanup and exit
            sys.exit(0)

if __name__ == "__main__":
    controller = VedaController()
    controller.bootstrap()
