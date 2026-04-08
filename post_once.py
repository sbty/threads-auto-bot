"""GitHub Actions用：指定アカウントで1投稿→終了"""
import sys
import time
import random
from datetime import datetime, timezone, timedelta

from ai_engine import AIEngine
from threads_client import ThreadsClient
from rss_fetcher import fetch_news
from database import Database
from config import Config

JST = timezone(timedelta(hours=9))


def post_for_account(account_config):
    """指定アカウントで1投稿"""
    prefix = account_config.prefix
    now = datetime.now(JST)

    print(f"{'='*50}")
    print(f"  {prefix}: {account_config.niche}")
    print(f"  Time: {now.strftime('%Y-%m-%d %H:%M')} JST")
    print(f"{'='*50}")

    if not account_config.is_active:
        print(f"❌ {prefix} is inactive. Check secrets.")
        sys.exit(1)

    topic = random.choice(account_config.topics)
    print(f"Topic: {topic}")

    # --- RSS取得（アカウント別）---
    print("\n--- Fetching RSS ---")
    headlines = fetch_news(topic, account=prefix)
    if headlines:
        for h in headlines:
            print(f"  {h}")
    else:
        print("  No articles found, continuing without RSS")

    # --- AI生成（アカウント別設定）---
    print("\n--- Generating post ---")
    db = Database(prefix)
    result = None
    for attempt in range(3):
        try:
            result = AIEngine.generate_post(
                custom_topic=topic,
                rss_context=headlines,
                account_niche=account_config.niche,
                account_tone=account_config.tone,
                account_db=db
            )
            if result and result.get("content"):
                break
        except Exception as e:
            print(f"  ⚠️ AI generation error (attempt {attempt+1}/3): {e}")
            time.sleep(5)
            
    if not result or not result.get("content"):
        print("❌ AI generation failed after 3 attempts")
        sys.exit(1)

    content = result["content"]
    print(f"Content: {content}")
    print(f"Topic: {result.get('topic', topic)}")

    # --- Threads投稿（アカウント別トークン）---
    print("\n--- Posting to Threads ---")
    client = ThreadsClient(
        access_token=account_config.access_token,
        user_id=account_config.user_id
    )
    post_id = None
    for attempt in range(3):
        try:
            post_id = client.create_text_post(content)
            if post_id:
                break
        except Exception as e:
            print(f"  ⚠️ Threads posting error (attempt {attempt+1}/3): {e}")
            time.sleep(5)

    if not post_id:
        print("❌ Post failed after 3 attempts")
        sys.exit(1)

    print(f"✅ Posted! ID: {post_id}")

    # --- DB保存 ---
    try:
        db.save_post(content, result.get("topic", topic), post_id)
    except Exception as e:
        print(f"⚠️ DB save error: {e}")


def main():
    # コマンドライン引数でアカウント指定
    if len(sys.argv) < 2:
        print("Usage: python post_once.py ACCOUNT1|ACCOUNT2")
        print("No account specified, posting for all active accounts")
        # 引数なしの場合は全アカウント（後方互換）
        for account in Config.get_active_accounts():
            post_for_account(account)
        return

    account_name = sys.argv[1].upper()

    # アカウント名から動的に取得
    account_map = {
        "ACCOUNT1": Config.ACCOUNT1,
        "ACCOUNT2": Config.ACCOUNT2,
        "ACCOUNT3": Config.ACCOUNT3,
    }

    if account_name in account_map:
        post_for_account(account_map[account_name])
    else:
        print(f"❌ Unknown account: {account_name}")
        sys.exit(1)


if __name__ == "__main__":
    main()