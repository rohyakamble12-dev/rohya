import sqlite3
import os
import json
import numpy as np
from datetime import datetime

class VedaMemory:
    def __init__(self, db_path="veda_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Semantic Memory (Facts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_key TEXT UNIQUE,
                fact_value TEXT,
                importance INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Episodic Memory (Events/Actions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                content TEXT,
                meta_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Custom Protocols
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol_name TEXT UNIQUE,
                commands TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Vector Store (Document Chunks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                chunk_text TEXT,
                embedding BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Knowledge Graph (Neural Links)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fact_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_a TEXT,
                relation TEXT,
                entity_b TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tasks Table (Persistence)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                priority INTEGER DEFAULT 1,
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    # --- Semantic Memory ---
    def store_fact(self, key, value, importance=1):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO user_facts (fact_key, fact_value, importance)
                VALUES (?, ?, ?)
            ''', (key.lower(), value, importance))
            conn.commit()
        finally:
            conn.close()

    def get_all_facts_summary(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT fact_key, fact_value FROM user_facts ORDER BY importance DESC, timestamp DESC LIMIT 20')
        rows = cursor.fetchall()
        conn.close()
        if not rows: return "No semantic facts recorded."
        return "\n".join([f"{row[0]}: {row[1]}" for row in rows])

    # --- Episodic Memory ---
    def store_episode(self, event_type, content, meta=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO episodes (event_type, content, meta_data)
                VALUES (?, ?, ?)
            ''', (event_type, content, json.dumps(meta) if meta else "{}"))
            conn.commit()
        finally:
            conn.close()

    def get_recent_episodes(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT event_type, content, timestamp FROM episodes ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows: return "No recent episodes."
        return "\n".join([f"[{r[2]}] {r[0]}: {r[1]}" for r in rows])

    # --- Vector Search (RAG) ---
    def store_document_chunk(self, source, text, embedding):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            emb_blob = np.array(embedding, dtype=np.float32).tobytes()
            cursor.execute('''
                INSERT INTO document_vectors (source, chunk_text, embedding)
                VALUES (?, ?, ?)
            ''', (source, text, emb_blob))
            conn.commit()
        finally:
            conn.close()

    def search_similar_chunks(self, query_embedding, limit=3, threshold=0.6):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT source, chunk_text, embedding FROM document_vectors')
        rows = cursor.fetchall()
        conn.close()

        if not rows: return []

        results = []
        query_vec = np.array(query_embedding, dtype=np.float32)
        for source, text, emb_blob in rows:
            emb_vec = np.frombuffer(emb_blob, dtype=np.float32)
            # Hybrid search could be added here by weighting keyword matches
            similarity = np.dot(query_vec, emb_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(emb_vec))
            if similarity >= threshold:
                results.append((source, text, similarity))

        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]

    # --- Knowledge Graph ---
    def link_intel(self, entity_a, relation, entity_b):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO fact_links (entity_a, relation, entity_b) VALUES (?, ?, ?)',
                         (entity_a.lower(), relation.lower(), entity_b.lower()))
            conn.commit()
            return f"Link: {entity_a} -> {relation} -> {entity_b}"
        finally: conn.close()

    def get_connected_intel(self, entity):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT relation, entity_b FROM fact_links WHERE entity_a = ?
            UNION
            SELECT relation, entity_a FROM fact_links WHERE entity_b = ?
        ''', (entity.lower(), entity.lower()))
        rows = cursor.fetchall()
        conn.close()
        if not rows: return f"No links for {entity}."
        return "\n".join([f"{entity} {r} {e}" for r, e in rows])

    def store_custom_protocol(self, name, commands):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO custom_protocols (protocol_name, commands) VALUES (?, ?)',
                         (name.lower(), json.dumps(commands)))
            conn.commit()
        finally: conn.close()

    def get_custom_protocol(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT commands FROM custom_protocols WHERE protocol_name = ?', (name.lower(),))
        result = cursor.fetchone()
        conn.close()
        return json.loads(result[0]) if result else None
