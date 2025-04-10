
import feedparser
import os
import random
from datetime import datetime

def fetch_feed_titles(feed_url, limit):
    feed = feedparser.parse(feed_url)
    titles = []
    for entry in feed.entries:
        if 'title' in entry:
            titles.append(entry.title.strip())
        if len(titles) >= limit:
            break
    return titles

# ============================
# Section 1: Fox News Headlines (100 total)
# ============================
fox_feeds = [
    "https://feeds.foxnews.com/foxnews/latest",
    "https://feeds.foxnews.com/foxnews/politics",
    "https://feeds.foxnews.com/foxnews/national",
    "https://feeds.foxnews.com/foxnews/world",
    "https://feeds.foxnews.com/foxnews/entertainment",
    "https://feeds.foxnews.com/foxnews/scitech",
    "https://feeds.foxnews.com/foxnews/health",
]
fox_headlines = []
seen = set()
for url in fox_feeds:
    titles = fetch_feed_titles(url, 100)
    for title in titles:
        if title not in seen:
            seen.add(title)
            fox_headlines.append(title)
fox_headlines = fox_headlines[:100]

# ============================
# Section 2: Global News Canada (25 headlines)
# ============================
canada_headlines = fetch_feed_titles("https://globalnews.ca/feed/", 25)

# ============================
# Section 3: World Headlines (25 headlines)
# ============================
world_headlines = fetch_feed_titles("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 25)

# ============================
# Section 4: Tech Headlines (25 headlines)
# ============================
tech_headlines = fetch_feed_titles("https://www.wired.com/feed/rss", 25)

# ============================
# Section 5: Satirical Headlines (20 headlines)
# ============================
satire_feeds = [
    "https://www.theonion.com/rss",
    "https://reductress.com/feed/",
    "https://clickhole.com/feed/",
]
satire_headlines = []
for url in satire_feeds:
    titles = fetch_feed_titles(url, 20)
    satire_headlines.extend(titles)
satire_headlines = satire_headlines[:20]

# ============================
# Section 6: Horoscopes (Aries, Cancer, Aquarius)
# ============================
horoscope_feed = "https://www.astrology.com/us/feed.ashx?topic=horoscope&sign={sign}"
signs = {"aries": "", "cancer": "", "aquarius": ""}
for sign in signs:
    parsed = feedparser.parse(horoscope_feed.format(sign=sign))
    if parsed.entries:
        signs[sign] = parsed.entries[0].summary.strip()

# ============================
# Section 7: Canucks News (RSS)
# ============================
canucks_feed = "https://www.nhl.com/canucks/rss/news"
canucks_news = fetch_feed_titles(canucks_feed, 10)

# ============================
# Output to File
# ============================
today_str = datetime.now().strftime("%Y-%m-%d")
output_filename = f"DailyDigest_{today_str}.txt"


with open(output_filename, "w", encoding="utf-8") as f:
    f.write("=== DAILY DIGEST ===\n")
    f.write(f"Date: {today_str}\n\n")

    f.write("== FOX NEWS HEADLINES (100) ==\n")
    for i, title in enumerate(fox_headlines, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

    f.write("== GLOBAL NEWS CANADA (25) ==\n")
    for i, title in enumerate(canada_headlines, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

    f.write("== WORLD HEADLINES (25) ==\n")
    for i, title in enumerate(world_headlines, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

    f.write("== TECH HEADLINES (25) ==\n")
    for i, title in enumerate(tech_headlines, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

    f.write("== SATIRICAL HEADLINES (20) ==\n")
    for i, title in enumerate(satire_headlines, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

    f.write("== HOROSCOPES ==\n")
    for sign, horoscope in signs.items():
        f.write(f"{sign.capitalize()}: {horoscope}\n")
    f.write("\n")

    f.write("== CANUCKS NEWS (10) ==\n")
    for i, title in enumerate(canucks_news, 1):
        f.write(f"{i}. {title}\n")
    f.write("\n")

print(f"✅ Daily Digest script ready to write to {output_filename}")
