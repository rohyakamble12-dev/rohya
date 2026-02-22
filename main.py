import sys
from veda.ui.gui import VedaGUI
from veda.core.assistant import VedaAssistant

def main():
    import logging
    # Define callbacks for the GUI
    def on_send(message):
        try:
            assistant.process_command(message)
        except Exception as e:
            logging.error(f"Error processing command: {e}")
            gui.update_chat("System", f"Command Error: {e}")

    def on_voice():
        try:
            assistant.listen_and_process()
        except Exception as e:
            logging.error(f"Error in voice interaction: {e}")
            gui.reset_voice_button()

    def on_upload(file_path):
        try:
            assistant.process_file(file_path)
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            gui.update_chat("System", f"File Processing Error: {e}")

    def on_closing():
        try:
            assistant.shutdown()
        except: pass

    # Create GUI
    try:
        gui = VedaGUI(
            on_send_callback=on_send,
            on_voice_callback=on_voice,
            on_upload_callback=on_upload,
            on_closing_callback=on_closing
        )
    except Exception as e:
        print(f"CRITICAL: Failed to create GUI: {e}")
        return

    # Initialize Assistant with GUI reference
    try:
        global assistant
        assistant = VedaAssistant(gui)
    except Exception as e:
        logging.critical(f"Failed to initialize Veda core: {e}")
        gui.update_chat("CRITICAL", f"Initialization failed: {e}")

    # Link GUI protocol changes to assistant
    gui.protocol_callback = assistant.sync_protocols

    # Background Listeners via ThreadManager
    from veda.utils.threads import manager as thread_manager

    def background_listener():
        result = assistant.voice.listen_for_wake_word("veda")
        if result:
            if result.lower() == "veda":
                gui.after(0, gui.trigger_voice)
            else:
                command = result.lower().replace("veda", "").strip()
                if command:
                    gui.after(0, lambda cmd=command: gui.update_chat("You", cmd))
                    gui.after(0, lambda cmd=command: assistant.process_command(cmd))

    # Enable "Hey Veda" wake word listener with sleep throttling (0.1s)
    thread_manager.run_with_throttle("WakeWordListener", background_listener, interval=0.1)

    # Enable Global Hotkeys
    try:
        import keyboard
        import os
        keyboard.add_hotkey('alt+v', lambda: gui.after(0, gui.trigger_voice))
        keyboard.add_hotkey('ctrl+alt+k', lambda: os._exit(1))
    except Exception as e:
        from veda.utils.logger import logger
        logger.warning(f"Failed to register global hotkeys: {e}")

    # Start the GUI main loop
    gui.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Veda shutting down...")
        sys.exit()
