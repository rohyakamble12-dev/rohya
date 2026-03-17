import sqlite3
import os
import logging
from datetime import datetime

class VedaMemory:
    def __init__(self, db_path="veda/veda.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macros (
                name TEXT PRIMARY KEY,
                sequence TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT,
                category TEXT DEFAULT 'general',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def log_interaction(self, role, content):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO interactions (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()

    def get_context(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT role, content FROM interactions ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def add_todo(self, task):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO todos (task) VALUES (?)", (task,))
        conn.commit(); conn.close()

    def get_todos(self):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT id, task FROM todos WHERE status='pending'").fetchall()
        conn.close()
        return rows

    def complete_todo(self, todo_id):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE todos SET status='completed' WHERE id=?", (todo_id,))
        conn.commit(); conn.close()

    def add_fact(self, fact):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO user_facts (fact) VALUES (?)", (fact,))
        conn.commit(); conn.close()

    def search_facts(self, query):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT fact FROM user_facts WHERE fact LIKE ?", (f"%{query}%",)).fetchall()
        conn.close()
        return [r[0] for r in rows]

    def save_state(self, key, value):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO system_state (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit(); conn.close()

    def load_state(self, key, default=None):
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT value FROM system_state WHERE key=?", (key,)).fetchone()
        conn.close()
        return row[0] if row else default
