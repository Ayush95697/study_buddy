"""
core/aggregate.py — Groups raw DB events into labelled sessions.
"""
from datetime import datetime, timezone
from core.db import db
from collector.config import POLLING_INTERVAL, SESSION_GAP_THRESHOLD


def aggregate_sessions(target_date: str, gap_threshold_sec: int = SESSION_GAP_THRESHOLD):
    """
    Merge consecutive events with the same label into sessions.

    Args:
        target_date:       YYYY-MM-DD local date string.
        gap_threshold_sec: Max gap (seconds) between events before starting a new session.

    Returns:
        List of session dicts: {start_time, end_time, duration_sec, app, label}
    """
    raw_events = db.fetch_daily_events(target_date)
    if not raw_events:
        return []

    def _parse(ts_str):
        """Parse ISO timestamp — handles both offset-aware and naive strings."""
        ts_str = ts_str.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(ts_str)
        except ValueError:
            return datetime.fromisoformat(ts_str + "+00:00")

    sessions = []
    first = raw_events[0]
    current = {
        "start_time": _parse(first["timestamp"]),
        "end_time":   _parse(first["timestamp"]),
        "app":        first["app"],
        "label":      first["label"],
    }

    for event in raw_events[1:]:
        event_time = _parse(event["timestamp"])
        gap = (event_time - current["end_time"]).total_seconds()

        same_label = event["label"] == current["label"]
        within_gap = gap <= gap_threshold_sec

        if same_label and within_gap:
            current["end_time"] = event_time
        else:
            _close_session(current, sessions)
            current = {
                "start_time": event_time,
                "end_time":   event_time,
                "app":        event["app"],
                "label":      event["label"],
            }

    _close_session(current, sessions)
    return sessions


def _close_session(session: dict, sessions: list):
    """Compute duration and append session. Minimum duration = one polling interval."""
    raw_duration = (session["end_time"] - session["start_time"]).total_seconds()
    session["duration_sec"] = max(raw_duration, POLLING_INTERVAL)
    sessions.append(session)