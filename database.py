import sqlite3
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                content TEXT,
                topic TEXT,
                posted_at TIMESTAMP,
                likes INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                used_count INTEGER DEFAULT 0,
                avg_engagement REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS performance_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_posts INTEGER,
                total_likes INTEGER,
                total_impressions INTEGER,
                follower_count INTEGER
            );
        """)
        self.conn.commit()

    def save_post(self, thread_id, content, topic):
        self.conn.execute(
            "INSERT INTO posts (thread_id, content, topic, posted_at) VALUES (?, ?, ?, ?)",
            (thread_id, content, topic, datetime.now().isoformat())
        )
        self.conn.commit()

    def get_recent_posts(self, limit=20):
        cursor = self.conn.execute(
            "SELECT content, topic, likes FROM posts ORDER BY posted_at DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

    def get_top_performing_topics(self, limit=5):
        cursor = self.conn.execute("""
            SELECT topic, AVG(likes + replies) as avg_engagement
            FROM posts WHERE likes > 0
            GROUP BY topic ORDER BY avg_engagement DESC LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def update_post_metrics(self, thread_id, likes, replies, impressions):
        self.conn.execute("""
            UPDATE posts SET likes=?, replies=?, impressions=?
            WHERE thread_id=?
        """, (likes, replies, impressions, thread_id))
        self.conn.commit()