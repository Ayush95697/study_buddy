import json
from datetime import datetime


def generate_daily_report(sessions, target_date):
    """
    Calculates stats and generates a personality-driven message.
    """
    total_focus = sum(s['duration_sec'] for s in sessions if s['label'] == 'focus')
    total_distract = sum(s['duration_sec'] for s in sessions if s['label'] == 'distraction')

    # Calculate Context Switches (How many times you changed labels)
    switches = len(sessions) - 1 if len(sessions) > 0 else 0

    focus_hours = round(total_focus / 3600, 2)
    distract_hours = round(total_distract / 3600, 2)

    # Personality Logic
    if total_focus > total_distract * 2:
        mood = "🔥 ELITE DISCIPLINE"
        msg = f"Locked in for {focus_hours}h. Your AI/ML research is progressing well."
    elif total_distract > total_focus:
        mood = "🤡 BRAIN ROT DETECTED"
        msg = f"You spent {distract_hours}h on distractions. This isn't how you finish Study Buddy."
    else:
        mood = "⚖️ MID PERFORMANCE"
        msg = "Average day. You need more deep work sessions and fewer tab-switches."

    report_text = f"""
*STUDY BUDDY REPORT - {target_date}*
Status: {mood}

✅ Focus: {focus_hours}h
❌ Distraction: {distract_hours}h
🔄 Context Switches: {switches}

"{msg}"
    """

    summary_json = json.dumps({
        "focus_sec": total_focus,
        "distract_sec": total_distract,
        "switches": switches
    })

    return report_text, summary_json