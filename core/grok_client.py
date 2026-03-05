"""
core/grok_client.py — Thin wrapper around the Groq API with retry logic.
"""
import os
import logging
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Lazy singleton — created on first call so missing env vars only crash at use-time
_client_instance = None


def get_client() -> "GroqClient":
    global _client_instance
    if _client_instance is None:
        _client_instance = GroqClient()
    return _client_instance


class GroqClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or _load_from_config()
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not set. Add it to your .env file or environment."
            )
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._client = Groq(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_reply(self, messages: list, temperature: float = 0.7) -> str:
        """
        Send a list of OpenAI-format messages to Groq and return the reply string.
        Retries up to 3 times with exponential back-off on transient errors.
        """
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=500,
        )
        return completion.choices[0].message.content


def _load_from_config():
    """Fallback: try importing GROQ_API_KEY from root config.py."""
    try:
        from config import GROQ_API_KEY
        return GROQ_API_KEY
    except Exception:
        return None