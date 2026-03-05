"""
core/memory_store.py — Stores and retrieves Telegram conversation history.
"""
import json
import logging
from datetime import datetime, timedelta, date
from core.db import db

logger = logging.getLogger(__name__)


class MemoryStore:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history

    def add_interaction(self, chat_id, role: str, text: str):
        """Persist a user message or bot reply."""
        query = """
            INSERT INTO chat_history (chat_id, role, text, timestamp)
            VALUES (?, ?, ?, ?)
        """
        db.execute_custom(query, (str(chat_id), role, text, datetime.now().isoformat()))

    def get_recent_chat(self, chat_id) -> list:
        """
        Return last N messages for this chat_id in chronological order
        (oldest → newest) ready to pass as an OpenAI-style messages list.
        """
        query = """
            SELECT role, text FROM chat_history
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT ?
        """
        rows = db.fetch_custom(query, (str(chat_id), self.max_history))
        # Reverse so oldest message is first
        return [{"role": r["role"], "content": r["text"]} for r in reversed(rows)]

    def get_weekly_trend(self) -> list:
        """
        Return the last 7 daily summaries (all users) for trend context.
        """
        seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        query = """
            SELECT day, summary_json FROM daily_reports
            WHERE day >= ?
            ORDER BY day ASC
        """
        rows = db.fetch_custom(query, (seven_days_ago,))
        trend = []
        for r in rows:
            try:
                data = json.loads(r["summary_json"])
                metrics = data.get("metrics", data)  # handle both summary shapes
                top_apps = data.get("top_apps", [])
                trend.append({
                    "date":       r["day"],
                    "focus_h":    round(metrics.get("focus_hours", metrics.get("focus_sec", 0) / 3600), 1),
                    "distract_h": round(metrics.get("distraction_hours", metrics.get("distract_sec", 0) / 3600), 1),
                    "top_apps":   top_apps,
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Skipping malformed summary_json for day %s: %s", r["day"], e)
        if trend:
            return trend

        # Fallback: no persisted summaries yet. Build a lightweight trend directly
        # from raw events via aggregation and the same summary logic used for
        # daily reports. This keeps the LLM from seeing raw events while still
        # giving it meaningful metrics even before /today has been called.
        try:
            from core.aggregate import aggregate_sessions
            from core.context_builder import context_builder
        except Exception as e:
            logger.error("Unable to import aggregation modules for weekly trend: %s", e)
            return []

        fallback_trend: list = []
        start_date = (datetime.now() - timedelta(days=7)).date()
        end_date = datetime.now().date()
        current = start_date

        while current <= end_date:
            day_str = current.isoformat()
            sessions = aggregate_sessions(day_str)
            if sessions:
                summary = context_builder.build_summary(sessions, day_str) or {}
                metrics = summary.get("metrics", {})
                focus_h = round(metrics.get("focus_hours", metrics.get("focus_sec", 0) / 3600), 1)
                distract_h = round(metrics.get("distraction_hours", metrics.get("distract_sec", 0) / 3600), 1)
                top_apps = summary.get("top_apps", [])
                fallback_trend.append(
                    {
                        "date":       day_str,
                        "focus_h":    focus_h,
                        "distract_h": distract_h,
                        "top_apps":   top_apps,
                    }
                )
            current += timedelta(days=1)

        return fallback_trend


memory = MemoryStore()