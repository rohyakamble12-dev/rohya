import sqlite3
from veda.features.base import VedaPlugin, PermissionTier

class TaskPlugin(VedaPlugin):
    def setup(self):
        self.register_intent("todo_add", self.add_todo, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"], "additionalProperties": False})
        self.register_intent("todo_list", self.get_todos, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {}, "additionalProperties": False})
        self.register_intent("todo_complete", self.complete_todo, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"], "additionalProperties": False})
        self.register_intent("pomodoro", self.start_pomodoro, PermissionTier.SAFE,
                            input_schema={"type": "object", "properties": {"duration": {"type": "integer"}}, "additionalProperties": False})

    def add_todo(self, params):
        content = params.get("task", "")
        priority = params.get("priority", 1)
        due = params.get("due", "Soon")

        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        # Secure initialization of task sector
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, priority INTEGER, due_date TEXT, completed INTEGER DEFAULT 0)''')
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
        idx = params.get("task_id")
        conn = sqlite3.connect(self.assistant.llm.memory.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (idx,))
        conn.commit()
        conn.close()
        return f"Task {idx} finalized."

    def start_pomodoro(self, params):
        """Active time management."""
        duration = params.get("duration", 25)
        self.assistant.process_command(f"set_timer minutes={duration} label='Pomodoro'", is_subcommand=True)
        return f"Pomodoro cycle established for {duration} minutes. Focus, Sir."
