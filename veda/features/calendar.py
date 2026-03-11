import sqlite3
import datetime
import os

class CalendarPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.db_path = "veda/storage/calendar.db"
        # Ensure tactical storage exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, date TEXT, time TEXT)')
            conn.close()
        except Exception as e:
            print(f"[SYSTEM]: Calendar initialization link unstable: {e}")

    def register_intents(self):
        return {
            "calendar_add": self.add_event,
            "calendar_list": self.list_events
        }

    def add_event(self, params):
        title = params.get("title")
        if not title: return "Intelligence missing for event title."
        date = params.get("date", datetime.date.today().isoformat())
        time = params.get("time", "12:00")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO events (title, date, time) VALUES (?, ?, ?)", (title, date, time))
            conn.commit()
            conn.close()
            return f"Event logged: {title} on {date} at {time}."
        except Exception as e:
            return f"Log failure: {e}"

    def list_events(self, params=None):
        try:
            conn = sqlite3.connect(self.db_path)
            rows = conn.execute("SELECT title, date, time FROM events ORDER BY date ASC").fetchall()
            conn.close()
            if not rows: return "The schedule is clear, Operator."

            schedule = "\n".join([f"- {r[0]}: {r[1]} @ {r[2]}" for r in rows[:5]])
            return f"Upcoming tactical schedule:\n{schedule}"
        except Exception as e:
            return f"Schedule retrieval link broken: {e}"
