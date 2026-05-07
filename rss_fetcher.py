import feedparser
import random
import urllib.request
import ssl
import socket

socket.setdefaulttimeout(10)


# アカウント1: カルチャー＆ライフスタイル（音楽,生活,最新ガジェット・ライフハック）
ACCOUNT1_FEEDS = {
    "音楽": [
        "https://news.google.com/rss/search?q=%E9%9F%B3%E6%A5%BD&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "海外サッカー": [
        "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E3%82%B5%E3%83%83%E3%82%AB%E3%83%BC&hl=ja&gl=JP&ceid=JP:ja",
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
        "https://news.google.com/rss/search?q=BGM+%E3%81%8A%E3%81%99%E3%81%99%E3%82%81&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "心を落ち着かせる音楽": [
        "https://news.google.com/rss/search?q=%E7%99%92%E3%82%84%E3%81%97+%E9%9F%B3%E6%A5%BD&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "名曲との出会い": [
        "https://news.google.com/rss/search?q=%E5%90%8D%E6%9B%B2+%E9%9F%B3%E6%A5%BD&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "日常を彩る音楽": [
        "https://news.google.com/rss/search?q=%E9%9F%B3%E6%A5%BD+%E3%83%97%E3%83%AC%E3%82%A4%E3%83%AA%E3%82%B9%E3%83%88&hl=ja&gl=JP&ceid=JP:ja",
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
    
    context = ssl._create_unverified_context()

    for url in feeds:
        try:
            # タイムアウトとUser-Agentを設定してハングを防ぐ
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                content = response.read()
                feed = feedparser.parse(content)
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