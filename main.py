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
    # global is used to ensure accessibility within callbacks if needed
    global assistant
    assistant = VedaAssistant(gui)

    # Optional: Start background wake-word listener
    import threading
    def background_listener():
        while True:
            # Note: requires properly configured hardware link
            if assistant.voice.listen_for_wake_word("veda"):
                gui.after(0, gui.trigger_voice)

    # Start the GUI main loop
    gui.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM]: Veda interface offline. Terminating links...")
        sys.exit()
