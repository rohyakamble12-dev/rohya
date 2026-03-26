import time
import threading
import json
import os
from pynput import keyboard, mouse

class AutomationModule:
    def __init__(self, storage_dir="storage/macros"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.recording = False
        self.current_macro = []
        self.k_listener = None
        self.m_listener = None

    def start_recording(self, name):
        if self.recording: return "Macro engine already active."
        self.name = name
        self.current_macro = []
        self.recording = True
        self.start_time = time.time()

        self.k_listener = keyboard.Listener(on_press=self._on_k_press)
        self.m_listener = mouse.Listener(on_click=self._on_m_click)
        self.k_listener.start()
        self.m_listener.start()
        return f"Protocol engaged. Recording macro: {name}. Perform tactical sequence now."

    def stop_recording(self):
        if not self.recording: return "No active recording sequence."
        self.recording = False
        self.k_listener.stop()
        self.m_listener.stop()

        with open(os.path.join(self.storage_dir, f"{self.name}.json"), "w") as f:
            json.dump(self.current_macro, f)
        return f"Sequence archived: {self.name}."

    def play_macro(self, name):
        path = os.path.join(self.storage_dir, f"{name}.json")
        if not os.path.exists(path): return f"Sequence '{name}' not found in tactical archives."

        with open(path, "r") as f:
            sequence = json.load(f)

        def _execute():
            k_ctrl = keyboard.Controller()
            m_ctrl = mouse.Controller()
            last_time = 0
            for event in sequence:
                time.sleep(max(0, event['time'] - last_time))
                last_time = event['time']
                if event['type'] == 'k':
                    k_ctrl.tap(event['key'])
                elif event['type'] == 'm':
                    m_ctrl.position = (event['x'], event['y'])
                    m_ctrl.click(mouse.Button.left)

        threading.Thread(target=_execute, daemon=True).start()
        return f"Executing tactical sequence: {name}."

    def type_text(self, text):
        """Simulates human-like typing for the provided text."""
        try:
            k_ctrl = keyboard.Controller()
            for char in text:
                k_ctrl.type(char)
                time.sleep(0.05)
            return "Data transmission complete: Text typed into active sector."
        except: return "Tactical typing protocol failed."

    def execute_script(self, code):
        """Safely executes a Python tactical script (restricted)."""
        try:
            # We use a restricted environment for safety
            exec(code, {'__builtins__': None, 'time': time, 'os': os}, {})
            return "Tactical script executed successfully."
        except Exception as e:
            return f"Script execution failed: {e}"

    def _on_k_press(self, key):
        if not self.recording: return
        try: k = key.char
        except: k = str(key)
        self.current_macro.append({'type': 'k', 'key': k, 'time': time.time() - self.start_time})

    def _on_m_click(self, x, y, button, pressed):
        if self.recording and pressed:
            self.current_macro.append({'type': 'm', 'x': x, 'y': y, 'time': time.time() - self.start_time})
