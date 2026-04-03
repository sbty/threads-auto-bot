import sqlite3
from datetime import datetime
from config import Config


class Database:
    def __init__(self, account_prefix="ACCOUNT1"):
        self.account_prefix = account_prefix
        self.table_name = f"posts_{account_prefix.lower()}"
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(Config.DB_PATH)
        c = conn.cursor()
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                topic TEXT,
                post_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_post(self, content, topic, post_id=None):
        conn = sqlite3.connect(Config.DB_PATH)
        c = conn.cursor()
        c.execute(f'''
            INSERT INTO {self.table_name} (content, topic, post_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (content, topic, post_id, datetime.now()))
        conn.commit()
        conn.close()
        print(f"  💾 Saved to {self.table_name}")
    
    def get_recent_posts(self, limit=10):
        conn = sqlite3.connect(Config.DB_PATH)
        c = conn.cursor()
        c.execute(f'''
            SELECT content, topic, created_at 
            FROM {self.table_name} 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        results = c.fetchall()
        conn.close()
        return results

    def get_top_performing_topics(self, limit=5):
        """よく投稿しているトピックを取得"""
        conn = sqlite3.connect(Config.DB_PATH)
        c = conn.cursor()
        c.execute(f'''
            SELECT topic, COUNT(*) as count
            FROM {self.table_name}
            WHERE topic IS NOT NULL
            GROUP BY topic
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        results = c.fetchall()
        conn.close()
        return results