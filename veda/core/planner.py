import re

class TacticalFastPath:
    def __init__(self):
        # Define patterns for survival mode (instant extraction without LLM)
        self.patterns = {
            "set_volume": [
                r"set volume to (\d+)",
                r"volume (\d+)",
                r"change volume to (\d+)"
            ],
            "set_brightness": [
                r"set brightness to (\d+)",
                r"brightness (\d+)"
            ],
            "open_app": [
                r"open ([\w\s.-]+)",
                r"launch ([\w\s.-]+)",
                r"start ([\w\s.-]+)"
            ],
            "close_app": [
                r"close ([\w\s.-]+)",
                r"kill ([\w\s.-]+)",
                r"stop ([\w\s.-]+)"
            ],
            "find": [
                r"find ([\w\s.-]+)",
                r"search for ([\w\s.-]+)",
                r"where is ([\w\s.-]+)"
            ],
            "move": [
                r"move ([\w\s./\\]+) to ([\w\s./\\]+)"
            ],
            "add_task": [
                r"add ([\w\s.-]+) to my tasks",
                r"remind me to ([\w\s.-]+)"
            ],
            "list_tasks": [
                r"what are my tasks",
                r"show my tasks",
                r"list tasks"
            ],
            "set_mode": [
                r"set mode to ([\w\s]+)",
                r"switch to ([\w\s]+) mode",
                r"engage ([\w\s]+) protocol"
            ],
            "time": [
                r"what time",
                r"current time",
                r"the time"
            ],
            "date": [
                r"what day",
                r"what is the date",
                r"today's date"
            ],
            "screenshot": [
                r"take a screenshot",
                r"screenshot"
            ],
            "lock_pc": [
                r"lock my pc",
                r"lock the computer",
                r"lock pc"
            ],
            "weather": [
                r"weather in ([\w\s]+)",
                r"weather for ([\w\s]+)"
            ],
            "wiki_search": [
                r"who is ([\w\s.-]+)",
                r"what is ([\w\s.-]+)",
                r"search wikipedia for ([\w\s.-]+)"
            ],
            "calendar_add": [
                r"add ([\w\s.-]+) to my calendar",
                r"log event ([\w\s.-]+)"
            ],
            "calendar_list": [
                r"show my calendar",
                r"what is my schedule"
            ],
            "extract_pdf": [
                r"read pdf ([\w\s./\\]+)",
                r"extract text from ([\w\s./\\]+)"
            ],
            "power_off": [
                r"shutdown",
                r"power off",
                r"terminate system"
            ],
            "restart": [
                r"reboot",
                r"restart"
            ],
            "system_stats": [
                r"system status",
                r"system stats",
                r"show stats",
                r"how is the system"
            ],
            "news": [
                r"news",
                r"headlines",
                r"what's happening"
            ]
        }

    def extract(self, text):
        """Attempts to extract intent and params using regex."""
        text = text.lower().strip()

        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    params = {}
                    if intent == "set_volume" or intent == "set_brightness":
                        params["level"] = match.group(1)
                    elif intent == "open_app" or intent == "close_app":
                        params["app_name"] = match.group(1).strip()
                    elif intent == "find":
                        params["query"] = match.group(1).strip()
                    elif intent == "move":
                        params["source"] = match.group(1).strip()
                        params["destination"] = match.group(2).strip()
                    elif intent == "add_task":
                        params["task"] = match.group(1).strip()
                    elif intent == "set_mode":
                        params["mode"] = match.group(1).strip()
                    elif intent == "weather":
                        params["city"] = match.group(1).strip()

                    return {"intent": intent, "params": params, "confidence": 1.0}

        return None
