import os
from dotenv import load_dotenv

load_dotenv()


class AccountConfig:
    """単一アカウントの設定"""
    def __init__(self, prefix, default_niche="テクノロジー", default_tone="カジュアル", default_topics=None):
        self.prefix = prefix
        self.access_token = os.getenv(f"{prefix}_THREADS_ACCESS_TOKEN")
        self.user_id = os.getenv(f"{prefix}_THREADS_USER_ID")
        self.niche = os.getenv(f"{prefix}_NICHE", default_niche)
        self.tone = os.getenv(f"{prefix}_TONE", default_tone)
        self.topics = self._parse_topics(os.getenv(f"{prefix}_TOPICS", default_topics or "一般"))
        
        self.is_active = bool(self.access_token and self.user_id)
    
    def _parse_topics(self, topics_str):
        return [t.strip() for t in topics_str.split(",")]
    
    def __repr__(self):
        status = "✅ Active" if self.is_active else "❌ Inactive"
        return f"{self.prefix}: {status} | {self.niche} | topics: {len(self.topics)}"


class Config:
    """全体設定"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    THREADS_API_BASE = "https://graph.threads.net/v1.0"
    DB_PATH = "bot_database.db"
    POST_INTERVAL_HOURS = 6
    
    # アカウント定義
    ACCOUNT1 = AccountConfig(
        "ACCOUNT1",
        default_niche="心地よい日常とカルチャー",
        default_tone="カジュアルで知的、共感を誘う",
        default_topics="音楽,生活,最新ガジェット・ライフハック"
    )
    
    ACCOUNT2 = AccountConfig(
        "ACCOUNT2",
        default_niche="AIツール活用と生産性向上",
        default_tone="分かりやすくプロフェッショナル、箇条書きを活用",
        default_topics="ChatGPT活用法,最新AIツール,時短術"
    )

    ACCOUNT3 = AccountConfig(
        "ACCOUNT3",
        default_niche="プログラミングとエンジニアの日常",
        default_tone="親しみやすい、少し自虐的でユーモアがある、ゆるい本音",
        default_topics="エンジニアあるある,リモートワークのリアル,バグとの戦い"
    )
    
    ACCOUNT4 = AccountConfig(
        "ACCOUNT4",
        default_niche="音楽と日常、YouTubeクリエイターのリアル",
        default_tone="エモーショナルで本音ベース、音楽への愛や裏話を語り共感を生むトーン",
        default_topics="おすすめ作業用BGM,音楽制作の裏側,YouTube運営のリアル,日常を彩る音楽"
    )
    
    @classmethod
    def get_active_accounts(cls):
        """有効なアカウント一覧を返す"""
        accounts = [cls.ACCOUNT1, cls.ACCOUNT2, cls.ACCOUNT3, cls.ACCOUNT4]
        return [a for a in accounts if a.is_active]
    
    @classmethod
    def print_status(cls):
        """設定状況を表示"""
        print("=" * 50)
        print("設定状況")
        print("=" * 50)
        print(f"Gemini API: {'✅ 設定済み' if cls.GEMINI_API_KEY else '❌ 未設定'}")
        print(f"\nアカウント1: {cls.ACCOUNT1}")
        print(f"アカウント2: {cls.ACCOUNT2}")
        print(f"アカウント3: {cls.ACCOUNT3}")
        print(f"アカウント4: {cls.ACCOUNT4}")
        print(f"\n有効アカウント数: {len(cls.get_active_accounts())}")
        print("=" * 50)