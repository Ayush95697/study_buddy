import json
from core.db import db
from datetime import datetime, timedelta


class MemoryStore:
    def __init__(self, max_history=20):
        self.max_history = max_history

    def add_interaction(self, chat_id, role, text):
        """Stores a user message or a bot reply in the database."""
        query = "INSERT INTO chat_history (chat_id, role, text, timestamp) VALUES (?, ?, ?, ?)"
        timestamp = datetime.now().isoformat()
        db.execute_custom(query, (chat_id, role, text, timestamp))

    def get_recent_chat(self, chat_id):
        """Fetches the last N messages to give Groq 'Conversation Memory'."""
        query = "SELECT role, text FROM chat_history WHERE chat_id = ? ORDER BY id DESC LIMIT ?"
        rows = db.fetch_custom(query, (chat_id, self.max_history))
        # Reverse to get chronological order (Oldest -> Newest)
        return [{"role": r['role'], "content": r['text']} for r in reversed(rows)]

    def get_weekly_trend(self, chat_id):
        """Fetches the last 7 daily summaries for trend analysis."""
        query = "SELECT day, summary_json FROM daily_reports WHERE day >= ? ORDER BY day ASC"
        seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        rows = db.fetch_custom(query, (seven_days_ago,))

        trend = []
        for r in rows:
            data = json.loads(r['summary_json'])
            trend.append({
                "date": r['day'],
                "focus_h": round(data['focus_sec'] / 3600, 1),
                "distract_h": round(data['distract_sec'] / 3600, 1)
            })
        return trend


memory = MemoryStore()