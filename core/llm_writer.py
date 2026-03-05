"""
core/llm_writer.py — Generates Telegram-style reports and chat replies via Groq.
"""
import json
import logging

from core.context_builder import context_builder
from core.prompt_templates import (
    DAILY_REPORT_SYSTEM,
    DAILY_REPORT_USER_TEMPLATE,
    CHAT_REPLY_SYSTEM,
    CHAT_REPLY_USER_TEMPLATE,
)
from core.grok_client import get_client
from core.db import db

logger = logging.getLogger(__name__)

_MAX_TELEGRAM_LEN = 4000


def generate_ai_summary(sessions: list, target_date: str) -> tuple[str, str]:
    """
    Build a structured summary from sessions, pass it to Groq,
    store the result and return (report_text, summary_json_str).
    """
    summary = context_builder.build_summary(sessions, target_date)
    if not summary:
        return "No data available for this period.", "{}"

    m = summary["metrics"]
    user_msg = DAILY_REPORT_USER_TEMPLATE.format(
        date=target_date,
        focus_hours=m["focus_hours"],
        distract_hours=m["distraction_hours"],
        switches=m["context_switches"],
        streak_min=m["longest_streak_min"],
        top_apps=", ".join(a.get("app", "Unknown") for a in summary.get("top_apps", [])),
        insights="; ".join(summary["insights"]) or "None",
    )

    messages = [
        {"role": "system", "content": DAILY_REPORT_SYSTEM},
        {"role": "user",   "content": user_msg},
    ]

    try:
        report_text = get_client().generate_reply(messages)
    except Exception as e:
        logger.error("Groq generate_ai_summary failed: %s", e)
        report_text = _fallback_report(m, target_date)

    # Truncate for Telegram safety
    if len(report_text) > _MAX_TELEGRAM_LEN:
        report_text = report_text[:_MAX_TELEGRAM_LEN - 3] + "..."

    summary_json_str = json.dumps(summary)

    # Only persist summaries for real calendar dates (YYYY-MM-DD). Weekly or
    # ad‑hoc ranges such as "Past 7 Days" are generated on the fly and not
    # stored in the daily_reports table to keep that table strictly per‑day.
    if _looks_like_ymd_date(target_date):
        db.store_report(target_date, report_text, summary_json_str)

    return report_text, summary_json_str


def generate_chat_reply(query: str, context_json: str) -> str:
    """
    Answer a free-form productivity question using recent summary context.
    """
    user_msg = CHAT_REPLY_USER_TEMPLATE.format(
        context_json=context_json,
        user_query=query,
    )
    messages = [
        {"role": "system", "content": CHAT_REPLY_SYSTEM},
        {"role": "user",   "content": user_msg},
    ]
    try:
        return get_client().generate_reply(messages)
    except Exception as e:
        logger.error("Groq generate_chat_reply failed: %s", e)
        return "Sorry, I couldn't reach the AI right now. Try again in a moment."


def _fallback_report(metrics: dict, date: str) -> str:
    """Plain-text fallback when the Groq call fails."""
    return (
        f"📊 *Study Buddy — {date}*\n\n"
        f"✅ Focus: {metrics['focus_hours']}h\n"
        f"❌ Distraction: {metrics['distraction_hours']}h\n"
        f"🔄 Context switches: {metrics['context_switches']}\n"
        f"⏱ Longest streak: {metrics['longest_streak_min']}min\n\n"
        f"_(AI summary unavailable — showing raw metrics)_"
    )


def _looks_like_ymd_date(value: str) -> bool:
    """Return True if value looks like a YYYY-MM-DD date string."""
    if not isinstance(value, str) or len(value) != 10:
        return False
    parts = value.split("-")
    if len(parts) != 3:
        return False
    y, m, d = parts
    return all(part.isdigit() for part in (y, m, d))
