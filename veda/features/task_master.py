import sqlite3
from veda.features.base import VedaPlugin, PermissionTier

class TaskPlugin(VedaPlugin):
    def __init__(self, assistant):
        super().__init__(assistant)
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
        return f"Task logged: {content} (P{priority})."

    def get_todos(self, params):
        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, priority, due_date FROM tasks WHERE completed = 0 ORDER BY priority DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows: return "No pending tasks."
        res = "Task List:\n"
        for r in rows:
            res += f"{r[0]}. [P{r[2]}] {r[1]} (Due: {r[3]})\n"
        return res

    def complete_todo(self, params):
        idx = params.get("index")
        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (idx,))
        conn.commit()
        conn.close()
        return f"Task {idx} finalized."

    def start_pomodoro(self, params):
        # Existing logic...
        return "Pomodoro active."
