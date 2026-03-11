import sqlite3

class MemoryManager:
    def __init__(self, db_name='memory_manager.db'):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY,
            fact TEXT NOT NULL
        )''')

        self.cur.execute('''CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY,
            episode TEXT NOT NULL
        )''')

        self.conn.commit()

    def store_fact(self, fact):
        self.cur.execute('INSERT INTO facts (fact) VALUES (?)', (fact,))
        self.conn.commit()

    def store_episode(self, episode):
        self.cur.execute('INSERT INTO episodes (episode) VALUES (?)', (episode,))
        self.conn.commit()

    def fetch_facts(self):
        self.cur.execute('SELECT * FROM facts')
        return self.cur.fetchall()

    def fetch_episodes(self):
        self.cur.execute('SELECT * FROM episodes')
        return self.cur.fetchall()

    def close(self):
        self.conn.close()  

if __name__ == '__main__':
    memory = MemoryManager()
    # Example usage
    memory.store_fact('The sky is blue.')
    memory.store_episode('Episode 1: Beginning of everything.')
    print(memory.fetch_facts())
    print(memory.fetch_episodes())
    memory.close()