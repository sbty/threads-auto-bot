import schedule
import time
import random
from datetime import datetime
from config import Config
from ai_engine import AIEngine
from threads_client import ThreadsClient
from rss_fetcher import fetch_news
from database import Database


class AccountBot:
    """単一アカウントのBot管理"""
    def __init__(self, account_config):
        self.config = account_config
        self.client = ThreadsClient(
            access_token=account_config.access_token,
            user_id=account_config.user_id
        )
        self.db = Database(account_config.prefix)  # アカウント別DB
        
        
    def get_today_topic(self):
        """日付ベースでトピックローテーション"""
        day = datetime.now().timetuple().tm_yday
        return self.config.topics[day % len(self.config.topics)]
    
    def generate_post(self, topic, rss_headlines):
        """アカウント別設定でAI生成"""
        return AIEngine.generate_post(
            custom_topic=topic,
            rss_context=rss_headlines,
            account_niche=self.config.niche,
            account_tone=self.config.tone,
            account_db=self.db
        )
    
    def auto_post(self):
        """投稿処理"""
        try:
            topic = self.get_today_topic()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            prefix = self.config.prefix
            print(f"\n[{now}] [{prefix}] Topic: {topic}")

            # RSS取得
            headlines = fetch_news(topic, account=self.config.prefix)
            if headlines:
                print(f"  RSS: {len(headlines)}件")
            
            # AI生成（アカウント別設定適用）
            try:
                result = self.generate_post(topic, headlines)
            except Exception as e:
                print(f"  ❌ AI generation failed: {e}")
                return
            
            if not result or not result.get("content"):
                print("  ❌ AI generation returned no content")
                return

            content = result["content"]
            print(f"  Generated: {content[:60]}...")

            # 投稿
            try:
                post_id = self.client.create_text_post(content)
            except Exception as e:
                print(f"  ❌ Threads posting failed: {e}")
                return
            
            if not post_id:
                print("  ❌ Post failed (no ID returned)")
                return

            print(f"  ✅ Posted! ID: {post_id}")

            # DB保存
            try:
                self.db.save_post(content, result.get("topic", topic), post_id)
            except Exception:
                pass

        except Exception as e:
            print(f"  ❌ ERROR [{self.config.prefix}]: {e}")


class MultiAccountBot:
    """複数アカウント管理"""
    def __init__(self):
        self.bots = []
        self.scheduled_times = {}  # アカウント別の今日の時間
        
        # 有効アカウントを初期化
        for cfg in Config.get_active_accounts():
            print(f"Initializing {cfg.prefix}: {cfg.niche}")
            self.bots.append(AccountBot(cfg))
        
        if not self.bots:
            raise ValueError("有効なアカウントがありません。.envを確認してください")
    
    def generate_times_for_account(self, prefix):
        """アカウント別にランダム時間を生成"""
        # 朝: 7-10時、夜: 17-21時（アカウントでずらす）
        offset = hash(prefix) % 3  # 0, 1, 2 のオフセット
        
        m_hour = 7 + offset
        m_min = random.randint(0, 59)
        
        e_hour = 17 + offset
        e_min = random.randint(0, 59)
        
        morning = f"{m_hour:02d}:{m_min:02d}"
        evening = f"{e_hour:02d}:{e_min:02d}"
        
        return morning, evening
    
    def schedule_today(self):
        """全アカウントの今日のスケジュールを設定"""
        schedule.clear("posts")
        
        print(f"\n{'='*50}")
        print(f"📅 Schedule for {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*50}")
        
        for bot in self.bots:
            cfg = bot.config
            morning, evening = self.generate_times_for_account(cfg.prefix)
            
            # スケジュール登録
            schedule.every().day.at(morning).do(bot.auto_post).tag("posts")
            schedule.every().day.at(evening).do(bot.auto_post).tag("posts")
            
            print(f"\n[{cfg.prefix}] {cfg.niche}")
            print(f"  🌅 Morning: {morning}")
            print(f"  🌙 Evening: {evening}")
            print(f"  Topics: {', '.join(cfg.topics)}")
        
        print(f"\n{'='*50}")
    
    def run(self):
        """メインループ"""
        Config.print_status()
        
        print(f"\nInitialized {len(self.bots)} account(s)")
        
        # 初回スケジュール
        self.schedule_today()
        
        # 毎日0:01に更新
        schedule.every().day.at("00:01").do(self.schedule_today)
        
        print("\n🤖 Bot is running. Press Ctrl+C to stop.\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n👋 Bot stopped.")


def main():
    multi_bot = MultiAccountBot()
    multi_bot.run()


if __name__ == "__main__":
    main()