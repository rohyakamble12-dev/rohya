import datetime

class VedaTools:
    def __init__(self, assistant):
        self.assistant = assistant

    def register_intents(self):
        return {
            "time": self.get_time,
            "date": self.get_date,
            "note": self.take_note
        }

    def take_note(self, params):
        text = params.get("text")
        with open("veda_notes.txt", "a") as f:
            f.write(f"[{datetime.datetime.now()}] {text}\n")
        return "Note saved."

    def get_time(self, params=None):
        return f"Time: {datetime.datetime.now().strftime('%I:%M %p')}"

    def get_date(self, params=None):
        return f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}"
