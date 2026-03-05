import requests
import os
import logging

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
MAX_LENGTH = 4000  # Leave a small buffer below the 4096 limit

def send_message(chat_id, text, parse_mode="Markdown"):
    """
    Sends a plain text message to a specific Telegram chat.
    Handles length limits and basic error reporting.
    """
    if not text:
        return

    # 1. Truncate if too long (Safety first)
    if len(text) > MAX_LENGTH:
        text = text[:MAX_LENGTH - 3] + "..."
        logging.warning(f"Message to {chat_id} was truncated due to length.")

    # 2. Prepare Payload
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode  # Allows bold/italic from LLM
    }

    # 3. Fire Request
    try:
        response = requests.post(BASE_URL, data=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return None