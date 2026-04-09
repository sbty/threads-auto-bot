import feedparser
import random


# アカウント1: カルチャー＆ライフスタイル（音楽,生活,最新ガジェット・ライフハック）
ACCOUNT1_FEEDS = {
    "音楽": [
        "https://natalie.mu/music/feed/news",
    ],
    "生活": [
        "https://www.lifehacker.jp/feed/index.xml",
    ],
    "最新ガジェット・ライフハック": [
        "https://www.gizmodo.jp/feed/index.xml",
    ],
}

# アカウント2: 有益AI・生産性（ChatGPT活用法,最新AIツール,時短術）
ACCOUNT2_FEEDS = {
    "ChatGPT活用法": [
        "https://ledge.ai/feed/",
    ],
    "最新AIツール": [
        "https://ainow.ai/feed/",
    ],
    "時短術": [
        "https://diamond.jp/list/rss",
    ],
}

# アカウント3: エンジニア共感・ポエム（エンジニアあるある,リモートワークのリアル,バグとの戦い）
ACCOUNT3_FEEDS = {
    "エンジニアあるある": [
        "https://b.hatena.ne.jp/hotentry/it.rss",
        "https://zenn.dev/topics/ポエム/feed",
    ],
    "リモートワークのリアル": [
        "https://qiita.com/popular-items/feed",
    ],
    "バグとの戦い": [
        "https://zenn.dev/feed",
        "https://dev.to/feed",
    ],
}

# アカウント4: 心地よい音楽とリスナーの日常
ACCOUNT4_FEEDS = {
    "おすすめ作業用BGM": [
        "https://note.com/topic/music/rss",
        "https://b.hatena.ne.jp/hotentry/entertainment.rss",
    ],
    "心を落ち着かせる音楽": [
        "https://note.com/topic/music/rss",
    ],
    "名曲との出会い": [
        "https://natalie.mu/music/feed/news",
    ],
    "日常を彩る音楽": [
        "https://natalie.mu/music/feed/news",
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