import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
from pathlib import Path

# ----------------------------
# Helper Functions
# ----------------------------
def fetch_feed_titles(feed_url, limit):
    """Return a list of headline strings from the specified RSS feed."""
    feed = feedparser.parse(feed_url)
    titles = []
    for entry in feed.entries:
        if 'title' in entry:
            titles.append(entry.title.strip())
        if len(titles) >= limit:
            break
    return titles

def fetch_feed_items(feed_url, limit):
    """
    Return a list of dictionaries with 'title' and 'link' from the feed.
    This is used for the hockey section so we can produce clickable links.
    """
    feed = feedparser.parse(feed_url)
    items = []
    for entry in feed.entries:
        if 'title' in entry and 'link' in entry:
            items.append({'title': entry.title.strip(), 'link': entry.link.strip()})
        if len(items) >= limit:
            break
    return items

def fetch_weather(city):
    """Return formatted weather info using wttr.in (in Celsius)."""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=10)
        return f"{city.capitalize()}: {response.text.strip()}"
    except Exception:
        return f"{city.capitalize()}: Weather unavailable"

def fetch_horoscope(sign):
    """Return today's horoscope for a given sign scraped from astrology.com."""
    try:
        url = f"https://www.astrology.com/horoscope/daily/{sign}.html"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 40 and not text.lower().startswith("by "):
                return text
        return f"{sign.capitalize()}: Horoscope unavailable"
    except Exception:
        return f"{sign.capitalize()}: Horoscope unavailable"

def filter_by_keyword(titles, keyword):
    """Filter a list of titles to those containing the given keyword."""
    return [title for title in titles if keyword.lower() in title.lower()]

# ----------------------------
# Date Setup
# ----------------------------
today = datetime.now().strftime("%A, %B %d, %Y")
today_str = datetime.now().strftime("%Y-%m-%d")

# ----------------------------
# News Feeds (Top 5 for each section)
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
fox_headlines = list({title for url in fox_feeds for title in fetch_feed_titles(url, 100)})[:5]

canada_headlines = fetch_feed_titles("https://globalnews.ca/feed/", 5)
world_headlines = fetch_feed_titles("https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 5)
tech_headlines = fetch_feed_titles("https://www.wired.com/feed/rss", 5)
satire_headlines = list({title for url in [
    "https://www.theonion.com/rss",
    "https://reductress.com/feed/",
    "https://clickhole.com/feed/"
] for title in fetch_feed_titles(url, 20)})[:5]

# ----------------------------
# Hockey Headlines from The Hockey Writers (complete set as links)
# ----------------------------
hockey_items = fetch_feed_items("https://thehockeywriters.com/feed/", 50)
# Also filter Canucks news from the hockey items:
canucks_items = [item for item in hockey_items if "canucks" in item["title"].lower()]

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
# Build Plain Text Digest (fallback)
# ----------------------------
plain_lines = [
    f"*{today}*\n",
    "== Fox News Headlines ==\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(fox_headlines)),
    "== Global News Canada ==\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(canada_headlines)),
    "== World Headlines (NYT) ==\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(world_headlines)),
    "== Tech (Wired) ==\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(tech_headlines)),
    "== Satirical Headlines ==\n" + "\n".join(f"{i+1}. {h}" for i, h in enumerate(satire_headlines)),
    "== Hockey Headlines (Complete) ==\n" + "\n".join(f"{i+1}. {item['title']}" for i, item in enumerate(hockey_items)),
    "== Canucks News ==\n" + "\n".join(f"{i+1}. {item['title']}" for i, item in enumerate(canucks_items)),
    "== Horoscopes ==\n" + f"Aries: {aries}\n\nCancer: {cancer}\n\nAquarius: {aquarius}",
    "== Weather ==\n" + "\n".join(weather_data),
]
plain_digest = "\n\n".join(plain_lines)

# ----------------------------
# Build HTML Digest (for email)
# ----------------------------
html_parts = [
    f"<h2>{today}</h2>",
    "<h3>Fox News Headlines</h3><ul>" + "".join(f"<li>{h}</li>" for h in fox_headlines) + "</ul>",
    "<h3>Global News Canada</h3><ul>" + "".join(f"<li>{h}</li>" for h in canada_headlines) + "</ul>",
    "<h3>World Headlines (NYT)</h3><ul>" + "".join(f"<li>{h}</li>" for h in world_headlines) + "</ul>",
    "<h3>Tech (Wired)</h3><ul>" + "".join(f"<li>{h}</li>" for h in tech_headlines) + "</ul>",
    "<h3>Satirical Headlines</h3><ul>" + "".join(f"<li>{h}</li>" for h in satire_headlines) + "</ul>",
    "<h3>Hockey Headlines (Complete)</h3><ul>" + "".join(f"<li>{item['title']}</li>" for item in hockey_items) + "</ul>",
    "<h3>Canucks News</h3><ul>" + "".join(f"<li><a href='{item['link']}' target='_blank'>{item['title']}</a></li>" for item in canucks_items) + "</ul>",
    "<h3>Horoscopes</h3>" +
      f"<p>Aries: {aries}</p>" +
      f"<p>Cancer: {cancer}</p>" +
      f"<p>Aquarius: {aquarius}</p>",
    "<h3>Weather</h3><ul>" + "".join(f"<li>{w}</li>" for w in weather_data) + "</ul>",
]
html_digest = "".join(html_parts)

# ----------------------------
# Save Plain Text Digest to File (for logging/backup)
# ----------------------------
output_path = Path(f"DailyDigest_{today_str}.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(plain_digest)
print(f"✅ Plain text digest saved to {output_path}")

# ----------------------------
# Email the Digest using HTML email (with plain text fallback)
# ----------------------------
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
receiver_emails = ["cmorrison.66@gmail.com", "Gerretteatta@gmail.com"]

msg = EmailMessage()
msg["Subject"] = f"🗞️ Your Daily Digest – {today}"
msg["From"] = EMAIL_USER
msg["To"] = ", ".join(receiver_emails)
msg.set_content(plain_digest)  # Plain text fallback
msg.add_alternative(html_digest, subtype="html")  # HTML version with links for hockey

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("✅ Digest email sent successfully!")
except Exception as e:
    print("❌ Failed to send digest email:", e)
