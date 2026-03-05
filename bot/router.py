import re
from core.aggregate import aggregate_sessions
from core.report import generate_daily_report
from core.llm_writer import generate_ai_summary  # Your Groq-powered writer
from datetime import date


def handle_message(chat_id, text):
    """
    The main routing logic. Returns the final string to send to the user.
    """
    text = text.strip().lower()

    # 1. HARDCODED COMMANDS (Fast, No LLM)
    if text == "/help":
        return ("Commands:\n"
                "/today - Get your stats for today\n"
                "/goal <hours> - Set your focus goal\n"
                "/strict on/off - Toggle strict mode\n"
                "Or just ask me anything about your productivity!")

    if text == "/today":
        # Get raw data -> Aggregate -> AI Summary
        today_str = date.today().isoformat()
        sessions = aggregate_sessions(today_str)

        if not sessions:
            return "No data for today yet. Get to work! 💻"

        # We use the LLM here because we want the "Personality"
        report_text, _ = generate_ai_summary(sessions, today_str)
        return report_text

    # 2. PARAMETERIZED COMMANDS (Regex based)
    # Match "/goal 3h" or "/goal 3"
    goal_match = re.match(r"/goal (\d+)", text)
    if goal_match:
        hours = goal_match.group(1)
        # TODO: Save to a simple config/DB table
        return f"✅ Goal updated: You're aiming for {hours}h of focus today."

    # 3. NATURAL LANGUAGE (The "Brain")
    # If it's not a slash command, it's a question for Groq.
    return handle_chat_query(text)


def handle_chat_query(query):
    """
    Uses Groq with 'CHAT_REPLY_TEMPLATE' to answer free-form questions.
    """
    # 1. Fetch recent context so Groq knows what you're talking about
    # 2. Format with prompt_templates.CHAT_REPLY_USER_TEMPLATE
    # 3. Return Groq's response
    return "I'm analyzing your recent patterns... (Groq integration goes here)"