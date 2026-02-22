import sqlite3
from veda.features.base import VedaPlugin, PermissionTier

class TaskPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("todo_add", self.add_todo, PermissionTier.SAFE)
        self.register_intent("todo_list", self.get_todos, PermissionTier.SAFE)
        self.register_intent("todo_complete", self.complete_todo, PermissionTier.SAFE)
        self.register_intent("pomodoro", self.start_pomodoro, PermissionTier.SAFE)

    def add_todo(self, params):
        content = params.get("task", "")
        priority = params.get("priority", 1)
        due = params.get("due", "Soon")

        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (content, priority, due_date) VALUES (?, ?, ?)", (content, priority, due))
        conn.commit()
        conn.close()
        return f"Task logged: {content}."

    def get_todos(self, params):
        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM tasks WHERE completed = 0")
        rows = cursor.fetchall()
        conn.close()
        if not rows: return "No pending tasks."
        return "Tasks:\n" + "\n".join([f"{r[0]}. {r[1]}" for r in rows])

    def complete_todo(self, params):
        idx = params.get("index")
        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (idx,))
        conn.commit()
        conn.close()
        return f"Task {idx} finalized."

    def start_pomodoro(self, params):
        return "Pomodoro sequence active."
