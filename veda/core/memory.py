import sqlite3
import os
import threading

class VedaMemory:
    def __init__(self, db_path="veda/storage/veda_memory.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()

    def set(self, key, value):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()

    def get(self, key, default=None):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else default

    def log_interaction(self, role, content):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO interactions (role, content) VALUES (?, ?)", (role, content))
            conn.commit()
            conn.close()
