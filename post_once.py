"""GitHub Actions用：1回実行→1投稿→終了"""
import sys
import random
from datetime import datetime, timezone, timedelta

from ai_engine import AIEngine
from threads_client import ThreadsClient
from rss_fetcher import fetch_news

JST = timezone(timedelta(hours=9))
TOPICS = ["音楽", "サッカー", "生活"]


def main():
    now = datetime.now(JST)
    topic = random.choice(TOPICS)

    print(f"=== {now.strftime('%Y-%m-%d %H:%M')} JST ===")
    print(f"=== Topic: {topic} ===\n")

    # --- RSS取得 ---
    print("--- Fetching RSS ---")
    headlines = fetch_news(topic)
    if not headlines:
        print("❌ No articles found")
        sys.exit(1)
    for h in headlines:
        print(f"  {h}")

    # --- AI生成 ---
    print("\n--- Generating post ---")
    result = AIEngine.generate_post(custom_topic=topic, rss_context=headlines)
    if not result or not result.get("content"):
        print("❌ AI generation failed")
        sys.exit(1)
    print(f"Content: {result['content']}")
    print(f"Topic: {result['topic']}")

    # --- Threads投稿 ---
    print("\n--- Posting to Threads ---")
    client = ThreadsClient()
    post_id = client.create_text_post(result["content"])
    if not post_id:
        print("❌ Post failed")
        sys.exit(1)
    print(f"✅ Posted! ID: {post_id}")


if __name__ == "__main__":
    main()