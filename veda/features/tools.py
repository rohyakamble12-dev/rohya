import datetime
from veda.features.base import VedaPlugin, PermissionTier

class ToolsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("time", self.get_time, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("date", self.get_date, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("note", self.take_note, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"], "additionalProperties": False})

    def get_time(self, params):
        return f"Current time: {datetime.datetime.now().strftime('%H:%M')}."

    def get_date(self, params):
        return f"Today: {datetime.datetime.now().strftime('%Y-%m-%d')}."

    def take_note(self, params):
        """Archives user thoughts into persistent neural memory."""
        content = params.get("content")
        if not content: return "Note body empty."

        # Ingest into long-term memory
        self.assistant.llm.memory.store_fact("User Note", content, importance=2)
        return "Note secured in long-term memory archives, Sir."
