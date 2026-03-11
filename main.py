import sys
from veda.ui.gui import VedaGUI
from veda.core.assistant import VedaAssistant

def main():
    # 1. Create a dummy/minimal GUI first if needed, but better to init Assistant first
    # However, Assistant needs GUI reference for some updates.
    # We solve this by passing a placeholder and updating it.

    class GUIProxy:
        def update_chat(self, *args): pass
        def update_protocol(self, *args): pass
        def after(self, *args): pass

    proxy = GUIProxy()
    assistant = VedaAssistant(proxy)

    # 2. Define real callbacks
    def on_send(message):
        return assistant.process_command(message)

    def on_voice():
        assistant.listen_and_process()

    # 3. Initialize real GUI with the assistant and callbacks
    gui = VedaGUI(on_send_callback=on_send, on_voice_callback=on_voice)

    # 4. Link Assistant to real GUI
    assistant.gui = gui

    # Optional: Start background wake-word listener
    import threading
    def background_listener():
        while True:
            try:
                if assistant.voice.listen_for_wake_word("veda"):
                    gui.after(0, gui.trigger_voice)
            except: pass

    # Start the GUI main loop
    print("[SYSTEM]: Veda Intelligence Online.")
    gui.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM]: Veda interface offline. Terminating links...")
        sys.exit()
