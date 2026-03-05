"""
bot/telegram_polling.py — Long-polling loop for the Telegram Bot API.
Do NOT run this directly; use `python run_bot.py` from the project root.
"""
import os
import sys
import time
import logging
import requests

from bot.router import handle_message
from notifier.telegram_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BOT] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _load_token_from_config():
    try:
        from config import TELEGRAM_BOT_TOKEN
        return TELEGRAM_BOT_TOKEN
    except Exception:
        return None


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or _load_token_from_config()
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_updates(offset: int | None = None) -> dict | None:
    """Long-poll getUpdates (30s server-side timeout)."""
    params = {
        "timeout": 30,
        "allowed_updates": ["message"],
    }
    if offset is not None:
        params["offset"] = offset
    try:
        resp = requests.get(
            BASE_URL + "getUpdates",
            params=params,
            timeout=40,  # slightly longer than Telegram's own timeout
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.warning("getUpdates failed: %s", e)
        return None


def run_polling():
    if not TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not set. Add it to your .env file and restart."
        )
        sys.exit(1)

    logger.info("Telegram Bot started. Waiting for messages...")
    offset = None
    backoff = 1  # seconds — grows on repeated failures, resets on success

    while True:
        updates = get_updates(offset)

        if updates is None:
            # Network error — back off before retrying
            logger.warning("Retrying in %ds...", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)  # cap at 60s
            continue

        backoff = 1  # reset on success

        if not updates.get("ok"):
            logger.error("Telegram API error: %s", updates)
            time.sleep(5)
            continue

        for update in updates.get("result", []):
            offset = update["update_id"] + 1  # advance offset — prevents reprocessing

            message = update.get("message")
            if not message:
                continue

            chat_id = message["chat"]["id"]
            text    = message.get("text", "").strip()
            user    = message.get("from", {}).get("username", "unknown")

            if not text:
                continue

            logger.info("@%s → %s", user, text[:60])

            try:
                reply = handle_message(chat_id, text)
            except Exception as e:
                logger.error("handler error for '%s': %s", text, e)
                reply = "⚠️ Something went wrong. Please try again."

            send_message(chat_id, reply)


if __name__ == "__main__":
    run_polling()