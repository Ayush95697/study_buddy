import os
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

class GroqClient:
    def __init__(self):
        # Read from environment variable for security
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")

        # Initialize the official Groq client
        self.client = Groq(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_reply(self, messages, model="llama-3.3-70b-versatile", temperature=0.7):
        """
        Talks to Groq's LPU inference engine.
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            raise

# Singleton instance
groq_client = GroqClient()