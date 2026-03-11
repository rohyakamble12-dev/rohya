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

    # Start the GUI main loop
    gui.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SYSTEM]: Veda interface offline. Terminating links...")
        sys.exit()
