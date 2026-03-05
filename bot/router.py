"""
bot/router.py — Central message router for the Telegram bot.
"""
import json
import logging
import re
from datetime import date, timedelta

from core.aggregate import aggregate_sessions
from core.llm_writer import generate_ai_summary, generate_chat_reply
from core.memory_store import memory

logger = logging.getLogger(__name__)


def handle_message(chat_id, text: str) -> str:
    """
    Route an incoming Telegram message and return the reply string.
    """
    stripped = text.strip()
    lower   = stripped.lower()

    # ── /help ─────────────────────────────────────────────────────────────────
    if lower == "/help":
        return (
            "📖 *Study Buddy Commands*\n\n"
            "/today — Today's AI productivity report\n"
            "/week  — Last 7 days recap\n"
            "/goal <hours> — Set your daily focus goal\n"
            "/strict on|off — Toggle strict mode\n\n"
            "Or just ask me anything about your productivity! 💬"
        )

    # ── /today ─────────────────────────────────────────────────────────────────
    if lower == "/today":
        today = date.today().isoformat()
        sessions = aggregate_sessions(today)
        if not sessions:
            return "No activity recorded yet today. Start your focus session! 🚀"
        report, _ = generate_ai_summary(sessions, today)
        return report

    # ── /week ──────────────────────────────────────────────────────────────────
    if lower == "/week":
        all_sessions = []
        for i in range(7):
            day = (date.today() - timedelta(days=i)).isoformat()
            all_sessions.extend(aggregate_sessions(day))
        if not all_sessions:
            return "Not enough data for a weekly report yet. Keep studying! 📚"
        report, _ = generate_ai_summary(all_sessions, "Past 7 Days")
        return f"📅 *Weekly Recap*\n\n{report}"

    # ── /goal <hours> ──────────────────────────────────────────────────────────
    goal_match = re.match(r"/goal\s+(\d+)", lower)
    if goal_match:
        hours = goal_match.group(1)
        from core.db import db
        db.update_user_setting(chat_id, "focus_goal", hours)
        return f"✅ Goal set: aiming for *{hours}h* of focus today."

    # ── /strict on|off ─────────────────────────────────────────────────────────
    strict_match = re.match(r"/strict\s+(on|off)", lower)
    if strict_match:
        status = 1 if strict_match.group(1) == "on" else 0
        from core.db import db
        db.update_user_setting(chat_id, "strict_mode", status)
        return f"🛡️ Strict Mode is now {'*ENABLED*' if status else '*DISABLED*'}."

    # ── Unknown slash command ──────────────────────────────────────────────────
    if stripped.startswith("/"):
        return "Unknown command. Type /help for available commands."

    # ── Free-text NLP question ─────────────────────────────────────────────────
    return _handle_chat_query(chat_id, stripped)


def _handle_chat_query(chat_id, query: str) -> str:
    """
    Answer a free-form productivity question using recent summaries as context.
    """
    # Build context from last weekly trend
    trend = memory.get_weekly_trend()
    if not trend:
        # No summaries have been generated yet — guide the user instead of
        # sending an empty context to the LLM (which leads to unhelpful replies).
        return (
            "I don't have any productivity history yet.\n\n"
            "Let the collector run for a while, then use /today or /week "
            "to generate your first report, and ask again."
        )
    context_json = json.dumps(trend, indent=2)

    # Store user message, call LLM, store reply
    memory.add_interaction(chat_id, "user", query)
    reply = generate_chat_reply(query, context_json)
    memory.add_interaction(chat_id, "assistant", reply)
    return reply