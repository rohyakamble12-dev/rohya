import time
import json
try:
    from pynput import keyboard, mouse
except ImportError:
    keyboard = None
    mouse = None
from veda.features.base import VedaPlugin, PermissionTier

class AutomationPlugin(VedaPlugin):
    def setup(self):
        self.recording = False
        self.events = []
        self.start_time = 0
        self.register_intent("start_recording", self.start_rec, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("stop_recording", self.stop_rec, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("play_macro", self.play_macro, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("mission_protocol", self.execute_mission, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"], "additionalProperties": False})

    def start_rec(self, params):
        if not keyboard or not mouse:
             return "Sovereign Block: Automation drivers (pynput) missing on this platform."
        self.recording = True
        self.events = []
        self.start_time = time.time()

        def on_click(x, y, button, pressed):
            if self.recording and pressed:
                self.events.append({"type": "mouse_click", "x": x, "y": y, "button": str(button), "time": time.time() - self.start_time})

        def on_press(key):
            if self.recording:
                try: k = key.char
                except AttributeError: k = str(key)
                self.events.append({"type": "kb_press", "key": k, "time": time.time() - self.start_time})

        self.mouse_listener = mouse.Listener(on_click=on_click)
        self.kb_listener = keyboard.Listener(on_press=on_press)
        self.mouse_listener.start()
        self.kb_listener.start()

        return "Learning user sequence..."

    def stop_rec(self, params):
        self.recording = False
        if hasattr(self, 'mouse_listener'): self.mouse_listener.stop()
        if hasattr(self, 'kb_listener'): self.kb_listener.stop()

        name = params.get("name", "last")
        with open(f"macro_{name}.json", "w") as f:
            json.dump(self.events, f)

        return f"Sequence secured as {name}."

    def play_macro(self, params):
        """Sequential tactical execution."""
        if not keyboard or not mouse:
             return "Sovereign Block: Automation drivers missing."
        name = params.get("name", "last")
        try:
            with open(f"macro_{name}.json", "r") as f:
                events = json.load(f)

            self.assistant.gui.update_chat("System", f"Executing macro sequence: {name}")
            mouse_ctrl = mouse.Controller()
            kb_ctrl = keyboard.Controller()

            last_time = events[0]["time"]
            for ev in events:
                time.sleep(max(0, ev["time"] - last_time))
                last_time = ev["time"]

                if ev["type"] == "mouse_move":
                    mouse_ctrl.position = (ev["x"], ev["y"])
                elif ev["type"] == "mouse_click":
                    mouse_ctrl.position = (ev["x"], ev["y"])
                    mouse_ctrl.click(mouse.Button.left if ev["button"] == "Button.left" else mouse.Button.right)
                elif ev["type"] == "kb_press":
                    try: kb_ctrl.press(ev["key"])
                    except: pass
                elif ev["type"] == "kb_release":
                    try: kb_ctrl.release(ev["key"])
                    except: pass

            return "Macro sequence playback complete."
        except Exception as e:
            return f"Macro playback failed: {e}"

    def execute_mission(self, params):
        name = params.get("name", "meeting").lower()
        missions = {"meeting": ["set volume 20", "open_app zoom"], "coding": ["open_app vscode"]}
        if name in missions:
            for c in missions[name]: self.assistant.process_command(c, is_subcommand=True)
            return f"Mission {name} complete."
        return "Target mission missing."
