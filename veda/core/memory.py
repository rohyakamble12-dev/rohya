import sqlite3
import os
import json
import numpy as np

class VedaMemory:
    def __init__(self, db_path="veda_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database and tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for user facts and preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_key TEXT UNIQUE,
                fact_value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for conversation history summary/long-term context
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_type TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for custom user protocols/macros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_name TEXT UNIQUE,
                commands TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for document embeddings (Vector Store)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                chunk_text TEXT,
                embedding BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def store_fact(self, key, value):
        """Stores or updates a user fact."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_facts (fact_key, fact_value)
                VALUES (?, ?)
            ''', (key.lower(), value))
            conn.commit()
        finally:
            conn.close()

    def get_fact(self, key):
        """Retrieves a specific fact."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT fact_value FROM user_facts WHERE fact_key = ?', (key.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_all_facts_summary(self):
        """Returns a string summary of all known facts for the LLM context."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT fact_key, fact_value FROM user_facts')
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "No personal facts known yet."
        return "\n".join([f"{row[0]}: {row[1]}" for row in rows])

    def store_custom_protocol(self, name, commands):
        """Stores a custom sequence of commands."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO custom_protocols (protocol_name, commands)
                VALUES (?, ?)
            ''', (name.lower(), json.dumps(commands) if isinstance(commands, list) else commands))
            conn.commit()
        finally:
            conn.close()

    def get_custom_protocol(self, name):
        """Retrieves a custom protocol's commands."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT commands FROM custom_protocols WHERE protocol_name = ?', (name.lower(),))
        result = cursor.fetchone()
        conn.close()
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        return None

    def store_document_chunk(self, source, text, embedding):
        """Stores a document chunk and its embedding."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Convert embedding list to binary for storage
            emb_blob = np.array(embedding, dtype=np.float32).tobytes()
            cursor.execute('''
                INSERT INTO document_vectors (source, chunk_text, embedding)
                VALUES (?, ?, ?)
            ''', (source, text, emb_blob))
            conn.commit()
        finally:
            conn.close()

    def search_similar_chunks(self, query_embedding, limit=3):
        """Finds the most similar chunks using cosine similarity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT source, chunk_text, embedding FROM document_vectors')
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        results = []
        query_vec = np.array(query_embedding, dtype=np.float32)

        for source, text, emb_blob in rows:
            emb_vec = np.frombuffer(emb_blob, dtype=np.float32)
            # Cosine similarity: (A . B) / (||A|| * ||B||)
            similarity = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec))
            results.append((source, text, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    def clear_memory(self):
        """Clears all stored data."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            self._init_db()
