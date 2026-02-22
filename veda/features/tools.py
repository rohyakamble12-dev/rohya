import datetime
from veda.features.base import VedaPlugin, PermissionTier

class ToolsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("time", self.get_time, PermissionTier.SAFE)
        self.register_intent("date", self.get_date, PermissionTier.SAFE)
        self.register_intent("note", self.take_note, PermissionTier.SAFE)

    def get_time(self, params):
        return f"Current time: {datetime.datetime.now().strftime('%H:%M')}."

    def get_date(self, params):
        return f"Today: {datetime.datetime.now().strftime('%Y-%m-%d')}."

    def take_note(self, params):
        return "Note appended to archives."
