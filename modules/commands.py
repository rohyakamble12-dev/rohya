from veda.modules.system import SystemModule
from veda.modules.intel import IntelModule
import logging
import os

class CommandRouter:
    def __init__(self, assistant):
        self.assistant = assistant
        self.system = SystemModule()
        self.intel = IntelModule()

    def route(self, intent_data):
        intent = intent_data.get("intent", "none")
        params = intent_data.get("params", {})

        if intent == "open_app":
            return self.system.open_app(params.get("app_name"))
        elif intent == "close_app":
            return self.system.close_app(params.get("app_name"))
        elif intent == "screenshot":
            return self.system.screenshot()
        elif intent == "system_health":
            return self.system.get_health()
        elif intent == "lock_pc":
            return self.system.lock_pc()
        elif intent == "web_search":
            return self.intel.search(params.get("query"))
        elif intent == "wikipedia":
            return self.intel.get_wiki(params.get("topic"))
        elif intent == "weather":
            return self.intel.get_weather(params.get("city"))
        elif intent == "add_todo":
            self.assistant.memory.add_todo(params.get("task"))
            return f"Task added: {params.get('task')}"
        elif intent == "show_todo":
            todos = self.assistant.memory.get_todos()
            if not todos: return "Todo list is clear."
            return "\n".join([f"{t[0]}. {t[1]}" for t in todos])

        return None
