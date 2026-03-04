from datetime import datetime
from core.db import db


def aggregate_sessions(target_date, gap_threshold_sec=300):
    """
    Groups raw 5-second events into continuous sessions.
    """
    raw_events = db.fetch_daily_events(target_date)
    if not raw_events:
        return []

    sessions = []
    if len(raw_events) == 0:
        return sessions

    # Start with the first event
    current_session = {
        "start_time": datetime.fromisoformat(raw_events[0]['timestamp']),
        "end_time": datetime.fromisoformat(raw_events[0]['timestamp']),
        "app": raw_events[0]['app'],
        "label": raw_events[0]['label']
    }

    for i in range(1, len(raw_events)):
        event = raw_events[i]
        event_time = datetime.fromisoformat(event['timestamp'])

        # Check if the event is the same activity and within the time gap
        time_diff = (event_time - current_session['end_time']).total_seconds()

        if event['label'] == current_session['label'] and time_diff <= gap_threshold_sec:
            # Continue the current session
            current_session['end_time'] = event_time
        else:
            # Close current session and start a new one
            duration = (current_session['end_time'] - current_session['start_time']).total_seconds()
            current_session['duration_sec'] = duration
            sessions.append(current_session)

            current_session = {
                "start_time": event_time,
                "end_time": event_time,
                "app": event['app'],
                "label": event['label']
            }

    # Add the last session
    duration = (current_session['end_time'] - current_session['start_time']).total_seconds()
    current_session['duration_sec'] = duration
    sessions.append(current_session)

    return sessions