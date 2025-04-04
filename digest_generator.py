
import feedparser
from datetime import datetime
import smtplib
from email.message import EmailMessage
 
# === Daily Digest Generation ===
today = datetime.now().strftime("%A, %B %d, %Y")

# Placeholder headline section
headlines = [
    "1. Sample headline 1",
    "2. Sample headline 2",
    "3. Sample headline 3"
]

# === HTML Content ===
html_content = f"""
<html>
<head>
  <meta charset="UTF-8">
  <title>Daily Digest – {today}</title>
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
  <h1>🗞️ Daily Digest</h1>
  <h2>{today}</h2>
  <h3>Top Headlines</h3>
  <ul>
    {''.join(f"<li>{line}</li>" for line in headlines)}
  </ul>
  <p>More updates soon!</p>
</body>
</html>
"""

# === Write to index.html ===
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ index.html updated.")

# === Send Email ===
sender_email = "cmorrison.66@gmail.com"
receiver_emails = ["cmorrison.66@gmail.com", "Gerretteatta@gmail.com"]
app_password = "olxk lmwm undt ngit"

msg = EmailMessage()
msg["Subject"] = f"🗞️ Your Daily Digest – {today}"
msg["From"] = sender_email
msg["To"] = ", ".join(receiver_emails)
msg.set_content("Your daily digest is ready. See the HTML version attached.")
msg.add_alternative(html_content, subtype="html")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)
    print("✅ Test email sent successfully!")
except Exception as e:
    print("❌ Failed to send email:", e)
