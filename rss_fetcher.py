import feedparser
import random


# アカウント1: カルチャー＆ライフスタイル（音楽,生活,最新ガジェット・ライフハック）
ACCOUNT1_FEEDS = {
    "音楽": [
        "https://pitchfork.com/rss/reviews/tracks/",
        "https://www.nme.com/feed",
    ],
    "海外サッカー": [
        "https://www.espn.com/espn/rss/soccer/news",
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
    ],
    "最新ガジェット・ライフハック": [
        "https://www.theverge.com/rss/index.xml",
        "https://lifehacker.com/rss",
    ],
}

# アカウント2: 有益AI・生産性（ChatGPT活用法,最新AIツール,時短術）
ACCOUNT2_FEEDS = {
    "ChatGPT活用法": [
        "https://venturebeat.com/category/ai/feed/",
    ],
    "最新AIツール": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
    ],
    "時短術": [
        "https://www.makeuseof.com/feed/",
    ],
}

# アカウント3: エンジニア注目の最新テック・開発トレンド
ACCOUNT3_FEEDS = {
    "最新テックニュース": [
        "https://techcrunch.com/feed/",
        "https://feeds.arstechnica.com/arstechnica/index",
    ],
    "開発トレンド": [
        "https://news.ycombinator.com/rss",
    ],
    "注目ライブラリ・ツール": [
        "https://dev.to/feed",
        "https://thenewstack.io/feed/",
    ],
    "技術の活用事例": [
        "https://www.technologyreview.com/feed/",
    ],
}

# アカウント4: 心地よい音楽とリスナーの日常
ACCOUNT4_FEEDS = {
    "おすすめ作業用BGM": [
        "https://www.npr.org/rss/rss.php?id=1039",
    ],
    "心を落ち着かせる音楽": [
        "https://pitchfork.com/rss/reviews/albums/",
    ],
    "名曲との出会い": [
        "https://www.rollingstone.com/music/music-news/feed/",
    ],
    "日常を彩る音楽": [
        "https://www.billboard.com/feed/",
    ],
}

# アカウント名 → フィード辞書のマッピング
ACCOUNT_FEEDS = {
    "account1": ACCOUNT1_FEEDS,
    "account2": ACCOUNT2_FEEDS,
    "account3": ACCOUNT3_FEEDS,
    "account4": ACCOUNT4_FEEDS,
}


def fetch_news(category, max_items=5, account="account1"):
    """指定アカウント・カテゴリのRSSから最新ニュースのタイトルを取得"""
    feeds_dict = ACCOUNT_FEEDS.get(account.lower(), ACCOUNT1_FEEDS)
    feeds = feeds_dict.get(category, [])
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
    for account_name, feeds_dict in ACCOUNT_FEEDS.items():
        print(f"\n{'='*40}")
        print(f"  {account_name}")
        print(f"{'='*40}")
        for cat in feeds_dict.keys():
            print(f"\n--- {cat} ---")
            news = fetch_news(cat, account=account_name)
            if news:
                for n in news:
                    print(f"  - {n}")
            else:
                print(f"  (取得できず)")