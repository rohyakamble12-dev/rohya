import time
import json
from pynput import keyboard, mouse
from veda.features.base import VedaPlugin, PermissionTier

class AutomationPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.recording = False
        self.events = []
        self.start_time = 0
        self.register_intent("start_recording", self.start_rec, PermissionTier.SAFE)
        self.register_intent("stop_recording", self.stop_rec, PermissionTier.SAFE)
        self.register_intent("play_macro", self.play_macro, PermissionTier.SAFE)
        self.register_intent("mission_protocol", self.execute_mission, PermissionTier.SAFE)

    def start_rec(self, params):
        self.events = []
        self.recording = True
        self.start_time = time.time()
        self.k_listener = keyboard.Listener(on_press=self._on_key)
        self.m_listener = mouse.Listener(on_click=self._on_click)
        self.k_listener.start()
        self.m_listener.start()
        return "Action recording initiated."

    def stop_rec(self, params):
        self.recording = False
        self.k_listener.stop()
        self.m_listener.stop()
        name = params.get("name", "default")
        with open(f"macro_{name}.json", 'w') as f:
            json.dump(self.events, f)
        return f"Macro '{name}' secured."

    def _on_key(self, key):
        if self.recording:
            k = key.char if hasattr(key, 'char') else str(key)
            self.events.append({'type': 'key', 'time': time.time() - self.start_time, 'data': k})

    def _on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            self.events.append({'type': 'click', 'time': time.time() - self.start_time, 'x': x, 'y': y})

    def play_macro(self, params):
        name = params.get("name", "default")
        return f"Replaying macro '{name}' (Simulation Mode)."

    def execute_mission(self, params):
        name = params.get("name", "meeting").lower()
        missions = {
            "meeting": ["set volume 20", "mute_toggle", "open_app zoom"],
            "coding": ["open_app vscode", "open_app chrome", "set_mode focus"]
        }
        if name not in missions: return "Mission not found."

        for cmd in missions[name]:
            self.assistant.process_command(cmd, is_subcommand=True)
        return f"Mission {name.upper()} executed."
