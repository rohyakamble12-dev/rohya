import sys
import threading
from veda.ui.gui import VedaGUI
from veda.core.assistant import VedaAssistant

class VedaController:
    def __init__(self):
        # 1. Initialize GUI first with empty callbacks
        self.gui = VedaGUI(
            on_send_callback=self.on_send,
            on_voice_callback=self.on_voice
        )

        # 2. Initialize Assistant with real GUI reference
        self.assistant = VedaAssistant(self.gui)

        # 3. Finalize setup
        self.setup_wake_word()
        print(f"[SYSTEM]: {self.assistant.ctx.get_summary()} | Intelligence Linked.")

    def on_send(self, message):
        return self.assistant.process_command(message)

    def on_voice(self):
        self.assistant.listen_and_process()

    def setup_wake_word(self):
        def background_listener():
            while True:
                try:
                    if self.assistant.voice.listen_for_wake_word("veda"):
                        self.gui.after(0, self.gui.trigger_voice)
                except: pass

        # threading.Thread(target=background_listener, daemon=True).start()

    def run(self):
        self.gui.mainloop()

def main():
    try:
        controller = VedaController()
        controller.run()
    except Exception as e:
        print(f"[CRITICAL]: Neural link collapsed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[SYSTEM]: Veda interface offline. Terminating links...")
        sys.exit()

if __name__ == "__main__":
    main()
