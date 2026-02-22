import datetime
from veda.features.base import VedaPlugin, PermissionTier

class ToolsPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
        self.register_intent("time", self.get_time, PermissionTier.SAFE)
        self.register_intent("date", self.get_date, PermissionTier.SAFE)
        self.register_intent("note", self.take_note, PermissionTier.SAFE)

    def get_time(self, params):
        return f"Time: {datetime.datetime.now().strftime('%H:%M')}."

    def get_date(self, params):
        return f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}."

    def take_note(self, params):
        text = params.get("text")
        with open("veda_notes.txt", "a") as f:
            f.write(f"[{datetime.datetime.now()}] {text}\n")
        return "Note secured."
