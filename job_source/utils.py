import requests

def send_telegram_notification(title, company, url, brief_description, location_name):
    TOKEN = "8577823415:AAFY06-T1Xpre4FZ6iclmkDwU-z7rhVdkKE"
    CHAT_ID = "6388235152"
    
    # We use Markdown to make the Title bold and the Link clickable
    message = (
        f"🚀 *New Job Alert!*\n\n"
        f"📌 *Role:* {title}\n\n"
        f"🏢 *Company:* {company}\n\n"
        f"🔗 [View Job Posting]({url})\n\n"
        f"\n\n📝 {brief_description}\n\n"
        f"📍 {location_name}"
    )
    
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(telegram_url, data=payload)
        # This will print the status to your terminal so you can see if it worked
        if response.status_code == 200:
            print("Telegram notification sent successfully!")
        else:
            print(f"Failed to send. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")