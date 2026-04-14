import sqlite3
import os
import json
import threading
import numpy as np
import hashlib
import base64
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from veda.utils.logger import logger

class VedaMemory:
    def __init__(self, db_path=None):
        # 0. Enforce strategic storage sector
        storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        os.makedirs(storage_dir, exist_ok=True)

        self.db_path = db_path or os.path.join(storage_dir, "veda_memory.db")
        self.write_lock = threading.Lock()
        self.init_lock = threading.Lock() # Final initialization lock

        # 1. Salt derivation: Use a machine-specific or persistent random salt
        self.salt_path = os.path.join(storage_dir, ".veda_salt")
        self.salt = self._get_or_create_salt()

        # Strategic Secret Retrieval
        secret = os.getenv("VEDA_TACTICAL_KEY", "StarkSovereign77")
        self.key = PBKDF2(secret, self.salt, dkLen=32, count=100000)

        with self.init_lock:
            self.is_locked = True
            self._verify_key()
            self._init_db()
            self._enable_wal()

    def _get_or_create_salt(self):
        if os.path.exists(self.salt_path):
            with open(self.salt_path, 'rb') as f: return f.read()
        salt = get_random_bytes(16)
        with open(self.salt_path, 'wb') as f: f.write(salt)
        return salt

    def _encrypt(self, text):
        """AES-256-GCM: Authenticated Encryption with integrity check."""
        if text is None: return None
        nonce = get_random_bytes(12)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(str(text).encode())
        return base64.b64encode(nonce + tag + ciphertext)

    def _decrypt(self, b64_data):
        """AES-256-GCM Decryption."""
        if not b64_data: return None
        try:
            data = base64.b64decode(b64_data)
            nonce = data[:12]
            tag = data[12:28]
            ciphertext = data[28:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except Exception as e:
            logger.error(f"Cryptographic Integrity Violation: {e}")
            return None

    def _hash_key(self, key):
        return hashlib.sha256(key.encode()).hexdigest()

    def _verify_key(self):
        """Verifies that the tactical key can decrypt a known signature."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS system_sig (id INTEGER PRIMARY KEY, sig BLOB)")
            cursor.execute("SELECT sig FROM system_sig WHERE id = 1")
            row = cursor.fetchone()

            test_val = "StarkSovereignVerified"
            if not row:
                enc = self._encrypt(test_val)
                cursor.execute("INSERT INTO system_sig (id, sig) VALUES (1, ?)", (enc,))
                conn.commit()
                self.is_locked = False
            else:
                dec = self._decrypt(row[0])
                if dec == test_val:
                    self.is_locked = False
                    logger.info("Memory Vault: Cryptographic link verified.")
                else:
                    self.is_locked = True
                    logger.critical("Memory Vault: ACCESS DENIED. Tactical key mismatch.")
        except Exception as e:
            logger.error(f"Memory Sector: Key verification failure: {e}")
            self.is_locked = True
        finally:
            if conn: conn.close()

    def _enable_wal(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        except Exception as e:
            logger.warning(f"Memory Sector: WAL optimization failure: {e}")
        finally:
            if conn: conn.close()

    def _init_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # 1. Tactical Migration: Check for legacy columns
            try:
                cursor.execute("SELECT fact_hash FROM user_facts LIMIT 1")
            except sqlite3.OperationalError:
                logger.warning("Memory Sector: Legacy schema detected. Rebuilding tactical vault.")
                cursor.execute("DROP TABLE IF EXISTS user_facts")
                cursor.execute("DROP TABLE IF EXISTS episodes")
                cursor.execute("DROP TABLE IF EXISTS document_vectors")

            # 2. Secure Schema Re-Initialization
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_hash TEXT UNIQUE,
                    fact_key BLOB,
                    fact_value BLOB,
                    importance INTEGER DEFAULT 1,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    content BLOB,
                    meta_data BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_vectors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source BLOB,
                    sector TEXT DEFAULT 'general',
                    chunk_text BLOB,
                    embedding BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE TABLE IF NOT EXISTS checkpoints (id INTEGER PRIMARY KEY AUTOINCREMENT, active_plan BLOB, execution_queue BLOB, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
            conn.commit()
        except Exception as e:
            logger.error(f"Memory Sector: DB initialization failure: {e}")
        finally:
            if conn: conn.close()

    def store_fact(self, key, value, importance=1):
        with self.write_lock:
            try:
                conn = sqlite3.connect(self.db_path, timeout=10) # Added timeout to handle locks
                cursor = conn.cursor()
                h = self._hash_key(key.lower())
                k_enc = self._encrypt(key)
                v_enc = self._encrypt(value)
                cursor.execute('INSERT OR REPLACE INTO user_facts (fact_hash, fact_key, fact_value, importance) VALUES (?, ?, ?, ?)',
                             (h, k_enc, v_enc, importance))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Memory Store Error: {e}")

    def get_all_facts_summary(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('SELECT fact_key, fact_value FROM user_facts ORDER BY importance DESC, timestamp DESC LIMIT 20')
            rows = cursor.fetchall()
            results = []
            for k_blob, v_blob in rows:
                k = self._decrypt(k_blob)
                v = self._decrypt(v_blob)
                if k and v: results.append(f"{k}: {v}")
            return "\n".join(results) if results else "No tactical knowledge found."
        except Exception as e:
            logger.error(f"Memory Sector: Fact retrieval failure: {e}")
            return "Knowledge retrieval compromised."
        finally:
            if conn: conn.close()

    def store_episode(self, event_type, content, meta=None):
        with self.write_lock:
            conn = None
            try:
                conn = sqlite3.connect(self.db_path, timeout=10)
                cursor = conn.cursor()
                c = self._encrypt(content)
                m = self._encrypt(json.dumps(meta or {}))
                cursor.execute('INSERT INTO episodes (event_type, content, meta_data) VALUES (?, ?, ?)', (event_type, c, m))
                conn.commit()
            except Exception as e:
                logger.error(f"Episode Store Error: {e}")
            finally:
                if conn: conn.close()

    def get_recent_episodes(self, limit=5):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('SELECT event_type, content FROM episodes ORDER BY timestamp DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            results = []
            for etype, c_blob in rows:
                c = self._decrypt(c_blob)
                if c: results.append(f"{etype}: {c}")
            return "\n".join(results) if results else "No recent episodes."
        except Exception as e:
            logger.error(f"Memory Sector: Episode retrieval failure: {e}")
            return "Memory retrieval compromised."
        finally:
            if conn: conn.close()

    def archive_old_data(self, days=30):
        logger.info(f"Memory: Enforcing retention policy ({days} days).")
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM episodes WHERE timestamp < datetime('now', ?)", (f'-{days} days',))
            cursor.execute("UPDATE user_facts SET importance = importance - 1 WHERE timestamp < datetime('now', ?) AND importance > 0", (f'-{days} days',))
            conn.commit()
        except Exception as e:
            logger.error(f"Archival Failure: {e}")
        finally:
            if conn: conn.close()

    def save_checkpoint(self, active_plan, execution_queue):
        # Performance: Run checkpointing in a background thread to avoid stalling the execution loop
        def _bg_save():
            with self.write_lock:
                try:
                    conn = sqlite3.connect(self.db_path, timeout=10)
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM checkpoints')
                    p = self._encrypt(json.dumps(active_plan))
                    q = self._encrypt(json.dumps(execution_queue))
                    cursor.execute('INSERT INTO checkpoints (active_plan, execution_queue) VALUES (?, ?)', (p, q))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.error(f"Checkpoint Error: {e}")

        threading.Thread(target=_bg_save, daemon=True).start()

    def get_last_checkpoint(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('SELECT active_plan, execution_queue FROM checkpoints ORDER BY timestamp DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                p = self._decrypt(row[0])
                q = self._decrypt(row[1])
                if p and q: return json.loads(p), json.loads(q)
        except Exception as e:
            logger.error(f"Memory Sector: Checkpoint retrieval failure: {e}")
        finally:
            if conn: conn.close()
        return None, None

    def clear_checkpoint(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM checkpoints')
            conn.commit()
        except Exception as e:
            logger.error(f"Memory Sector: Checkpoint purge failure: {e}")
        finally:
            if conn: conn.close()
