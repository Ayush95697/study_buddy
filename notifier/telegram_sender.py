import requests
import os
import logging


def _load_token_from_config():
    """Fallback loader so config.py-based tokens also work."""
    try:
        from config import TELEGRAM_BOT_TOKEN
        return TELEGRAM_BOT_TOKEN
    except Exception:
        return None


# Configuration (env takes precedence, then config.py)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or _load_token_from_config()
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage" if TOKEN else None
MAX_LENGTH = 4000  # Leave a small buffer below the 4096 limit


def send_message(chat_id, text, parse_mode="Markdown"):
    """
    Sends a plain text message to a specific Telegram chat.
    Handles length limits and basic error reporting.
    """
    if not text:
        return

    if not TOKEN or not BASE_URL:
        logging.error("Cannot send Telegram message: TELEGRAM_BOT_TOKEN is not configured.")
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