import sys
from veda.ui.gui import VedaGUI
from veda.core.assistant import VedaAssistant

def main():
    # Define callbacks for the GUI
    def on_send(message):
        assistant.process_command(message)

    def on_voice():
        assistant.listen_and_process()

    # Create GUI
    gui = VedaGUI(on_send_callback=on_send, on_voice_callback=on_voice)

    # Initialize Assistant with GUI reference
    global assistant
    assistant = VedaAssistant(gui)

    # Link GUI protocol changes to assistant
    gui.protocol_callback = assistant.sync_protocols

    # Optional: Start background wake-word listener
    import threading
    def background_listener():
        while True:
            if assistant.voice.listen_for_wake_word("veda"):
                # Use root.after to safely trigger GUI from background thread
                gui.after(0, gui.trigger_voice)

    # Enable "Hey Veda" wake word listener in the background
    threading.Thread(target=background_listener, daemon=True).start()

    # Start the GUI main loop
    gui.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Veda shutting down...")
        sys.exit()
