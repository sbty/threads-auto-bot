import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
    THREADS_USER_ID = os.getenv("THREADS_USER_ID")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", 6))
    ACCOUNT_NICHE = os.getenv("ACCOUNT_NICHE", "テクノロジー")
    ACCOUNT_TONE = os.getenv("ACCOUNT_TONE", "カジュアルで知的")
    THREADS_API_BASE = "https://graph.threads.net/v1.0"
    DB_PATH = "bot_database.db"