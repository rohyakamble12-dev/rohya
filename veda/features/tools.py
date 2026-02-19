import datetime
import os

class VedaTools:
    @staticmethod
    def take_note(text):
        """Saves a note to a local file."""
        try:
            filename = "veda_notes.txt"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filename, "a") as f:
                f.write(f"[{timestamp}] {text}\n")
            return "I've saved that note for you."
        except Exception as e:
            return f"Failed to save note: {str(e)}"

    @staticmethod
    def get_time():
        """Returns the current time."""
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"

    @staticmethod
    def get_date():
        """Returns today's date."""
        today = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today is {today}"
