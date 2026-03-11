import sqlite3
import datetime

class CalendarPlugin:
    def __init__(self, assistant):
        self.assistant = assistant
        self.db_path = "veda/storage/calendar.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, date TEXT, time TEXT)')
        conn.close()

    def register_intents(self):
        return {
            "calendar_add": self.add_event,
            "calendar_list": self.list_events
        }

    def add_event(self, params):
        title = params.get("title")
        date = params.get("date", datetime.date.today().isoformat())
        time = params.get("time", "12:00")

        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO events (title, date, time) VALUES (?, ?, ?)", (title, date, time))
        conn.commit()
        conn.close()
        return f"Event logged: {title} on {date} at {time}."

    def list_events(self, params=None):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT title, date, time FROM events ORDER BY date ASC").fetchall()
        conn.close()
        if not rows: return "The schedule is clear."

        schedule = "\n".join([f"- {r[0]}: {r[1]} @ {r[2]}" for r in rows[:5]])
        return f"Upcoming schedule:\n{schedule}"
