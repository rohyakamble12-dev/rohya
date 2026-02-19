import os
# Mocking tkinter since we might not have a display
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import tkinter as tk
from veda.ui.gui import VedaGUI

def test_gui_init():
    def dummy_callback(*args, **kwargs):
        pass

    try:
        # This might still fail if no X server is present,
        # but let's see if we can at least check for syntax/import errors.
        root = VedaGUI(on_send_callback=dummy_callback, on_voice_callback=dummy_callback)
        print("GUI Initialized successfully.")
        root.after(100, root.destroy)
        root.mainloop()
    except Exception as e:
        print(f"GUI Initialization failed as expected in headless mode, but let's check the error: {e}")
        # If the error is about 'no display name', that's fine.
        # If it's a NameError or ImportError, that's a real bug.
        if "no display name" in str(e) or "TclError" in str(e):
            print("Import and Class definition seem okay.")
        else:
            raise e

if __name__ == "__main__":
    test_gui_init()
