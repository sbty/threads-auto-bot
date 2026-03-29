import schedule
import time
import random
from datetime import datetime
from ai_engine import AIEngine
from threads_client import ThreadsClient
from rss_fetcher import fetch_news
from database import Database

TOPICS = ["音楽", "サッカー", "生活"]
client = ThreadsClient()
db = Database()


def get_today_topic():
    """日付ベースで毎日違うトピックに自動ローテーション"""
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def auto_post():
    """AI生成 + RSS参考 + Threads投稿"""
    try:
        topic = get_today_topic()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"\n[{now}] Posting about: {topic}")

        # RSS から最新ニュースを取得
        headlines = fetch_news(topic)
        if headlines:
            print(f"  RSS headlines found: {len(headlines)}")
            for h in headlines[:3]:
                print(f"    - {h}")
        else:
            print("  No RSS headlines (will generate without)")

        # AI でコンテンツ生成
        result = AIEngine.generate_post(custom_topic=topic, rss_context=headlines)
        content = result["content"]
        print(f"  Generated: {content[:80]}...")

        # Threads に投稿
        post_id = client.create_text_post(content)
        print(f"  Posted! ID: {post_id}")

        # DB に保存
        try:
            db.save_post(content, result.get("topic", topic))
        except Exception:
            print("  DB save skipped (method may not exist)")

    except Exception as e:
        print(f"  ERROR: {e}")


def schedule_today():
    """毎日ランダムな時刻で2回投稿をスケジュール"""
    schedule.clear("posts")

    # 朝: 7:00〜9:59 のランダム
    m_hour = random.randint(7, 9)
    m_min = random.randint(0, 59)
    morning = f"{m_hour:02d}:{m_min:02d}"

    # 夜: 18:00〜20:59 のランダム
    e_hour = random.randint(18, 20)
    e_min = random.randint(0, 59)
    evening = f"{e_hour:02d}:{e_min:02d}"

    schedule.every().day.at(morning).do(auto_post).tag("posts")
    schedule.every().day.at(evening).do(auto_post).tag("posts")

    topic = get_today_topic()
    print(f"\n=== Schedule for {datetime.now().strftime('%Y-%m-%d')} ===")
    print(f"  Topic:   {topic}")
    print(f"  Morning: {morning}")
    print(f"  Evening: {evening}")


def main():
    print("=" * 40)
    print("  Threads Auto Bot")
    print("  Topics: " + " / ".join(TOPICS))
    print("=" * 40)

    # 今日のスケジュールを設定
    schedule_today()

    # 毎日0:01に翌日のスケジュールを再設定
    schedule.every().day.at("00:01").do(schedule_today)

    print("\nBot is running. Press Ctrl+C to stop.")
    print("Waiting for scheduled times...\n")

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nBot stopped.")


if __name__ == "__main__":
    main()