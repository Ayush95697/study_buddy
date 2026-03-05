"""
bot/handlers.py — Thin wrappers kept for backward-compatibility.
All real logic now lives in bot/router.py.
"""
from bot.router import handle_message


def handle_today(chat_id):
    return handle_message(chat_id, "/today")


def handle_week(chat_id):
    return handle_message(chat_id, "/week")


def handle_set_goal(chat_id, goal_text):
    return handle_message(chat_id, f"/goal {goal_text}")


def handle_strict_mode(chat_id, mode):
    return handle_message(chat_id, f"/strict {mode}")