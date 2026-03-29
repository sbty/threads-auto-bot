import json
from ai_engine import AIEngine
from threads_client import ThreadsClient
from rss_fetcher import fetch_news
from datetime import datetime

TOPICS = ["音楽", "サッカー", "生活"]
day = datetime.now().timetuple().tm_yday
topic = TOPICS[day % len(TOPICS)]

print(f"=== Today's topic: {topic} ===")

print("\n--- Fetching RSS ---")
headlines = fetch_news(topic)
for h in headlines:
    print(f"  {h}")

print("\n--- Generating post ---")
result = AIEngine.generate_post(custom_topic=topic, rss_context=headlines)
print(f"Content: {result['content']}")
print(f"Topic: {result['topic']}")

print("\n--- Posting to Threads ---")
client = ThreadsClient()
post_id = client.create_text_post(result["content"])
print(f"Posted! ID: {post_id}")