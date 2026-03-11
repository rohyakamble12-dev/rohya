import sqlite3

class TaskManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.db_path = "veda_memory.db"
        conn = sqlite3.connect(self.db_path)
        conn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT, status TEXT DEFAULT "pending")')
        conn.close()

    def register_intents(self):
        return {
            "add_task": self.add_task,
            "list_tasks": self.list_tasks
        }

    def add_task(self, params):
        task = params.get("task")
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
        conn.commit(); conn.close()
        return f"Task added: {task}"

    def list_tasks(self, params=None):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT task FROM tasks WHERE status='pending'").fetchall()
        conn.close()
        return "Tasks:\n" + "\n".join([r[0] for r in rows]) if rows else "No pending tasks."
