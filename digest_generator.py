import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
from pathlib import Path

def fetch_feed_titles(feed_url, limit):
    feed = feedparser.parse(feed_url)
    titles = []
    for entry in feed.entries:
        if 'title' in entry:
            titles.append(entry.title.strip())
        if len(titles) >= limit:
            break
    return titles

def fetch_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=10)
        return f"{city.capitalize()}: {response.text.strip()}"
    except Exception:
        return f"{city.capitalize()}: Weather unavailable"

def fetch_horoscope(sign):
    try:
        url = f"https://www.astrology.com/horoscope/daily/{sign}.html"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraph = soup.find("p")
        return paragraph.text.strip() if paragraph else f"{sign.capitalize()}: Horoscope unavailable"
    except Exception:
        return f"{sign.capitalize()}: Horoscope unavailable"

# ----------------------------
# Date Setup
# ----------------------------
today = datetime.now().strftime("%A, %B %d, %Y")
today_str = datetime.now().strftime("%Y-%m-%d")

# ----------------------------
# News Feeds Scraping
# ----------------------------
fox_feeds = [
    "https://feeds.foxnews.com/foxnews/latest",
    "https://feeds.foxnews.com/foxnews/politics",
    "https://feeds.foxnews.com/foxnews/national",
    "https://feeds.foxnews.com/foxnews/world",
    "https://feeds.foxnews.com/foxnews/entertainment",
    "https://feeds.foxnews.com/foxnews/scitech",
    "https://feeds.foxnews.com/foxnews/health",
]
fox_headlines = list({title for url in fox_feeds for title in fetch_feed_titles(url, 100)})[:100]

canada_headlines = fetch_feed_titles("https://globalnews.ca/feed/", 25)
world_headlines = fetch_feed_titles("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 25)
tech_headlines = fetch_feed_titles("https://www.wired.com/feed/rss", 25)

satire_feeds = [
    "https://www.theonion.com/rss",
    "https://reductress.com/feed/",
    "https://clickhole.com/feed/",
]
satire_headlines = list({title for url in satire_feeds for title in fetch_feed_titles(url, 20)})[:20]

nhl_headlines = fetch_feed_titles("https://www.nhl.com/rss/news.xml", 10)
canucks_headlines = fetch_feed_titles("https://www.nhl.com/canucks/rss/news.xml", 5)

# ----------------------------
# Horoscopes (live scrape)
# ----------------------------
aries = fetch_horoscope("aries")
cancer = fetch_horoscope("cancer")
aquarius = fetch_horoscope("aquarius")

# ----------------------------
# Weather (for selected cities)
# ----------------------------
weather_cities = ["vancouver", "victoria", "terrace", "smithers", "hazelton"]
weather_data = [fetch_weather(city) for city in weather_cities]

# ----------------------------
# Build Digest Content
# ----------------------------
lines = [
    f"*{today}*\n",
    "== Fox News Headlines ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(fox_headlines)],
    "\n== Global News Canada ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(canada_headlines)],
    "\n== World Headlines (NYT) ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(world_headlines)],
    "\n== Tech (Wired) ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(tech_headlines)],
    "\n== Satirical Headlines ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(satire_headlines)],
    "\n== NHL Headlines ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(nhl_headlines)],
    "\n== Canucks News ==\n",
    *[f"{i+1}. {h}" for i, h in enumerate(canucks_headlines)],
    "\n== Horoscopes ==\n",
    f"Aries: {aries}\nCancer: {cancer}\nAquarius: {aquarius}\n",
    "\n== Weather ==\n",
    *weather_data,
]

digest_text = "\n".join(lines)

# ----------------------------
# Write Digest to File (for logging/backup)
# ----------------------------
output_path = Path(f"DailyDigest_{today_str}.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(digest_text)
print(f"✅ Digest saved to {output_path}")

# ----------------------------
# Email the Digest directly (embed digest text in email body)
# ----------------------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
receiver_emails = ["cmorrison.66@gmail.com", "Gerretteatta@gmail.com"]

msg = EmailMessage()
msg["Subject"] = f"🗞️ Your Daily Digest – {today}"
msg["From"] = EMAIL_USER
msg["To"] = ", ".join(receiver_emails)
msg.set_content(digest_text)  # Embed digest text directly in the email body

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("✅ Digest email sent successfully!")
except Exception as e:
    print("❌ Failed to send digest email:", e)
