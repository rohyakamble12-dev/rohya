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
                r"start (?!pomodoro)([\w\s.-]+)"
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
            "calculate": [
                r"calculate (.*)",
                r"convert (.*)",
                r"math (.*)"
            ],
            "look_camera": [
                r"look through the camera",
                r"what am i looking at"
            ],
            "trigger_iot": [
                r"trigger iot",
                r"trigger smart home"
            ],
            "pomodoro": [
                r"start pomodoro (?:for )?(\d+) (?:mins|minutes)",
                r"pomodoro (\d+)"
            ],
            "system_health": [
                r"system health",
                r"mark 42 status",
                r"diagnostic report"
            ],
            "media_control": [
                r"play (?!.*song name)(.*)", # match 'play song' but not literal prompt cheat sheet
                r"pause",
                r"next",
                r"previous"
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
                    elif intent == "calculate":
                        params["query"] = match.group(1).strip()
                    elif intent == "pomodoro":
                        params["minutes"] = match.group(1).strip()
                    elif intent == "media_control":
                        if "play" in text and match.lastindex and match.lastindex >= 1:
                            # if it matches play (something), we might want to just start playing or open the song.
                            # For simplicity we just pass 'play' as action
                            params["action"] = "play"
                        elif "pause" in text:
                            params["action"] = "pause"
                        elif "next" in text:
                            params["action"] = "next"
                        elif "previous" in text:
                            params["action"] = "previous"

                    return {"intent": intent, "params": params, "confidence": 1.0}

        return None
