import feedparser
import random


RSS_FEEDS = {
    "音楽": [
        "https://natalie.mu/music/feed/news",
    ],
    "サッカー": [
        "https://www.soccer-king.jp/feed",
    ],
    "生活": [
        "https://www.lifehacker.jp/feed/index.xml",
    ],
}


def fetch_news(category, max_items=5):
    """指定カテゴリのRSSから最新ニュースのタイトルを取得"""
    feeds = RSS_FEEDS.get(category, [])
    articles = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "")
                if title:
                    articles.append(title)
        except Exception as e:
            print(f"RSS error ({url}): {e}")

    random.shuffle(articles)
    return articles[:max_items]


if __name__ == "__main__":
    for cat in ["音楽", "サッカー", "生活"]:
        print(f"\n=== {cat} ===")
        news = fetch_news(cat)
        for n in news:
            print(f"  - {n}")