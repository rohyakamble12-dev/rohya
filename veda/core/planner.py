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
                    elif intent == "weather":
                        params["city"] = match.group(1).strip()

                    return {"intent": intent, "params": params, "confidence": 1.0}

        return None
