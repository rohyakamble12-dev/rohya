from pynput import keyboard, mouse
import time
import threading
import json

class VedaAutomation:
    def __init__(self):
        self.recording = False
        self.events = []
        self.start_time = 0

    def start_recording(self):
        self.events = []
        self.recording = True
        self.start_time = time.time()

        # Start listeners
        self.key_listener = keyboard.Listener(on_press=self._on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self._on_click)

        self.key_listener.start()
        self.mouse_listener.start()
        return "Recording started. Perform the actions you want me to learn."

    def stop_recording(self, macro_name="default"):
        self.recording = False
        self.key_listener.stop()
        self.mouse_listener.stop()

        # Save to file
        with open(f"macro_{macro_name}.json", 'w') as f:
            json.dump(self.events, f)

        return f"Macro '{macro_name}' saved successfully."

    def _on_key_press(self, key):
        if not self.recording: return False
        try:
            k = key.char
        except AttributeError:
            k = str(key)
        self.events.append({'type': 'key', 'time': time.time() - self.start_time, 'data': k})

    def _on_click(self, x, y, button, pressed):
        if not self.recording: return False
        if pressed:
            self.events.append({'type': 'click', 'time': time.time() - self.start_time, 'x': x, 'y': y, 'button': str(button)})

    def play_macro(self, macro_name="default"):
        try:
            with open(f"macro_{macro_name}.json", 'r') as f:
                events = json.load(f)

            kb_controller = keyboard.Controller()
            m_controller = mouse.Controller()

            start_time = time.time()
            for event in events:
                delay = event['time'] - (time.time() - start_time)
                if delay > 0:
                    time.sleep(delay)

                if event['type'] == 'key':
                    # Simplified key playing
                    kb_controller.press(self._parse_key(event['data']))
                    kb_controller.release(self._parse_key(event['data']))
                elif event['type'] == 'click':
                    m_controller.position = (event['x'], event['y'])
                    m_controller.click(mouse.Button.left) # Defaulting to left for simplicity

            return f"Finished playing macro '{macro_name}'."
        except Exception as e:
            return f"Failed to play macro: {str(e)}"

    def _parse_key(self, key_str):
        if hasattr(keyboard.Key, key_str.replace('Key.', '')):
            return getattr(keyboard.Key, key_str.replace('Key.', ''))
        return key_str
