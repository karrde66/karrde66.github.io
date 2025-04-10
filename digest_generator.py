import feedparser
import os
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def fetch_feed_titles(feed_url, limit):
    feed = feedparser.parse(feed_url)
    titles = []
    seen = set()
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        if title and title not in seen:
            seen.add(title)
            titles.append(title)
        if len(titles) >= limit:
            break
    return titles

today_str = datetime.now().strftime("%A, %B %d, %Y")

# ============================ Fox News (100 headlines)
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
for url in fox_feeds:
    fox_headlines.extend(fetch_feed_titles(url, 30))
fox_headlines = fox_headlines[:100]

# ============================ Global News Canada (25)
canada_headlines = fetch_feed_titles("https://globalnews.ca/feed/", 25)

# ============================ NYT World (25)
world_headlines = fetch_feed_titles("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 25)

# ============================ Wired Tech (25)
tech_headlines = fetch_feed_titles("https://www.wired.com/feed/rss", 25)

# ============================ Satire (20)
satire_feeds = [
    "https://www.theonion.com/rss",
    "https://reductress.com/feed/",
    "https://clickhole.com/feed/",
]
satire_headlines = []
for url in satire_feeds:
    satire_headlines.extend(fetch_feed_titles(url, 10))
satire_headlines = satire_headlines[:20]

# ============================ NHL & Canucks (10)
nhl_headlines = fetch_feed_titles("https://www.nhl.com/rss/news.xml", 10)
canucks_headlines = fetch_feed_titles("https://www.nhl.com/canucks/rss/news", 5)

# ============================ Horoscope (Aries, Cancer, Aquarius)
aries = fetch_feed_titles("https://www.astrology.com/us/feed.ashx?sign=aries", 1)
cancer = fetch_feed_titles("https://www.astrology.com/us/feed.ashx?sign=cancer", 1)
aquarius = fetch_feed_titles("https://www.astrology.com/us/feed.ashx?sign=aquarius", 1)

# ============================ Build email body
digest = []
digest.append("📰 **Daily Digest**")
digest.append(f"**{today_str}**\n")

def section(title, items):
    digest.append(f"\n== {title} ==\n")
    for i, item in enumerate(items, 1):
        digest.append(f"{i}. {item}")

section("Fox News Headlines", fox_headlines)
section("Global News Canada", canada_headlines)
section("World Headlines (NYT)", world_headlines)
section("Tech (Wired)", tech_headlines)
section("Satirical Headlines", satire_headlines)
section("NHL Headlines", nhl_headlines)
section("Canucks News", canucks_headlines)

digest.append("\n== Horoscopes ==")
digest.append(f"Aries: {aries[0] if aries else 'Unavailable'}")
digest.append(f"Cancer: {cancer[0] if cancer else 'Unavailable'}")
digest.append(f"Aquarius: {aquarius[0] if aquarius else 'Unavailable'}")

digest_text = "\n".join(digest)

# ============================ Send Email
msg = MIMEText(digest_text)
msg["Subject"] = f"📰 Your Daily Digest – {today_str}"
msg["From"] = os.environ["EMAIL_USER"]
msg["To"] = "cmorrison.66@gmail.com"

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
    server.send_message(msg)

print("✅ Email sent to cmorrison.66@gmail.com and Gerrettetatta@gmail.com")
