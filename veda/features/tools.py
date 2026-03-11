import datetime
import os

class VedaTools:
    def __init__(self, assistant):
        self.assistant = assistant
        self.notes_file = "veda/storage/notes.txt"

    def register_intents(self):
        return {
            "time": self.get_time,
            "date": self.get_date,
            "note": self.take_note
        }

    def take_note(self, params):
        text = params.get("text")
        if not text: return "Note content missing."

        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        with open(self.notes_file, "a") as f:
            f.write(f"[{datetime.datetime.now()}] {text}\n")
        return "Note saved."

    def get_time(self, params=None):
        return f"Time: {datetime.datetime.now().strftime('%I:%M %p')}"

    def get_date(self, params=None):
        return f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}"
