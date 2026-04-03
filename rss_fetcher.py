import feedparser
import random


# アカウント1: machiru731（テクノロジー / 音楽,サッカー,生活）
ACCOUNT1_FEEDS = {
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

# アカウント2: yohei753（農業,AI,音楽）- 海外ソース
ACCOUNT2_FEEDS = {
    "農業": [
        "https://modernfarmer.com/feed/",
        "https://www.agweb.com/rss/news",
        "https://www.successfulfarming.com/feed",
    ],
    "AI": [
        "https://feeds.feedburner.com/mittechipreview",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
    ],
    "音楽": [
        "https://pitchfork.com/feed/feed-news/rss",
        "https://www.stereogum.com/feed/",
        "https://consequence.net/feed/",
    ],
}

# アカウント名 → フィード辞書のマッピング
ACCOUNT_FEEDS = {
    "account1": ACCOUNT1_FEEDS,
    "account2": ACCOUNT2_FEEDS,
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