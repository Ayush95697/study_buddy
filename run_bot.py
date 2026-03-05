"""
run_bot.py — Entry point for the Telegram bot.
Run from the project root: python run_bot.py
"""
import sys
import os

# Ensure project root is on the path so all imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

# Load .env first before other imports access os.getenv
import config

from bot.telegram_polling import run_polling

if __name__ == "__main__":
    run_polling()
