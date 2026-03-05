import requests
import time
import os

# Your Bot Token from @BotFather
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_updates(offset=None):
    """
    Calls getUpdates with a timeout for 'Long Polling'.
    """
    url = BASE_URL + "getUpdates"
    params = {
        "timeout": 30,  # Keeps connection open for 30s if no messages
        "offset": offset,
        "allowed_updates": ["message"]
    }
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Polling Error: {e}")
        return None


def run_polling():
    """
    The main loop that listens for messages.
    """
    offset = 0  # Keeps track of which messages we've already seen
    print("Telegram Bot Polling Started...")

    while True:
        updates = get_updates(offset)

        if updates and updates.get("ok"):
            for update in updates["result"]:
                # Update the offset so we don't see this message again
                offset = update["update_id"] + 1

                # Extract the core message data
                message = update.get("message")
                if not message: continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")
                username = message["from"].get("username", "Unknown")

                print(f"New Message from @{username}: {text}")

                # TODO: ROUTE TO HANDLER
                # handle_message(chat_id, text)

        # Small sleep to prevent CPU hogging if the API fails
        time.sleep(1)


if __name__ == "__main__":
    run_polling()