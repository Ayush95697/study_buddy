from core.db import db
from core.aggregate import aggregate_sessions
from core.llm_writer import generate_ai_summary
from datetime import date, timedelta


def handle_today(chat_id):
    """Logic for the /today command."""
    today_str = date.today().isoformat()
    sessions = aggregate_sessions(today_str)

    if not sessions:
        return "No activity recorded yet today. Start your focus session! 🚀"

    # Generate the fancy AI report
    report_text, _ = generate_ai_summary(sessions, today_str)
    return report_text


def handle_week(chat_id):
    """Aggregates the last 7 days of data."""
    all_sessions = []
    for i in range(7):
        day = (date.today() - timedelta(days=i)).isoformat()
        all_sessions.extend(aggregate_sessions(day))

    if not all_sessions:
        return "Not enough data for a weekly report yet."

    # You would use a 'weekly report' prompt template here
    report_text, _ = generate_ai_summary(all_sessions, "Past 7 Days")
    return f"📅 *Weekly Recap*\n\n{report_text}"


def handle_set_goal(chat_id, goal_text):
    """Stores the user's focus goal in the database."""
    # Simple extraction (e.g., from '3h' or '3')
    try:
        hours = int(''.join(filter(str.isdigit, goal_text)))
        # Update a 'settings' table in your DB (you may need to add this table in schema.py)
        db.update_user_setting(chat_id, "focus_goal", hours)
        return f"✅ Goal set! I'll track your progress toward {hours} hours of focus today."
    except ValueError:
        return "⚠️ Please provide a number, e.g., '/goal 4'."


def handle_strict_mode(chat_id, mode):
    """Toggles the 'Strict Mode' setting."""
    status = 1 if mode == "on" else 0
    db.update_user_setting(chat_id, "strict_mode", status)
    return f"🛡️ Strict Mode is now {'ENABLED' if status else 'DISABLED'}."