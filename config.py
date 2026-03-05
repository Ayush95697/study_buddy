"""
Root config — loads environment variables from .env (via python-dotenv).
Import this anywhere you need API keys or shared settings.
"""
import os
from dotenv import load_dotenv

# Load .env from the project root (wherever this file lives).
# `override=True` ensures that values in .env take precedence over any
# pre-existing environment variables, so updating .env is always respected.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
