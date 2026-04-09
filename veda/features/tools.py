import datetime
import json
from veda.features.base import VedaPlugin, PermissionTier

class ToolsPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("time", self.get_time, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("date", self.get_date, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("note", self.take_note, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"content": {"type": "string"}}, "required": ["content"], "additionalProperties": False})

        self.register_intent("format_json", self.format_json, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"], "additionalProperties": False})

        self.register_intent("word_count", self.word_count, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"], "additionalProperties": False})

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

    def format_json(self, params):
        """Pretty-prints a JSON string."""
        data = params.get("data", "")
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"

    def word_count(self, params):
        """Calculates text metrics."""
        text = params.get("text", "")
        lines = text.splitlines()
        words = text.split()
        return f"Metrics: {len(text)} chars | {len(words)} words | {len(lines)} lines."
