"""
core/context_builder.py — Converts aggregated sessions into privacy-safe JSON for the LLM.
"""
import json
from datetime import datetime
from collections import Counter


class ContextBuilder:
    def build_summary(self, sessions: list, target_date: str) -> dict | None:
        """
        Transforms session data into a structured JSON summary.
        Only app names (never raw window titles) reach the LLM.
        """
        if not sessions:
            return None

        totals = {"focus": 0.0, "distraction": 0.0, "away": 0.0, "neutral": 0.0}
        app_time: Counter = Counter()
        longest_streak = 0.0
        current_streak = 0.0
        switches = 0
        prev_label = None

        for session in sessions:
            label    = session["label"]
            duration = session["duration_sec"]

            if label in totals:
                totals[label] += duration

            # Privacy: only record app name (not title) for non-away sessions
            if label != "away":
                app_time[session["app"]] += duration

            # Longest continuous focus streak
            if label == "focus":
                current_streak += duration
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0.0

            if prev_label is not None and label != prev_label:
                switches += 1
            prev_label = label

        top_apps = [
            {"app": app, "time_min": round(sec / 60, 1)}
            for app, sec in app_time.most_common(3)
        ]

        return {
            "date": target_date,
            "metrics": {
                "focus_hours":       round(totals["focus"]       / 3600, 2),
                "distraction_hours": round(totals["distraction"] / 3600, 2),
                "away_hours":        round(totals["away"]        / 3600, 2),
                "longest_streak_min": round(longest_streak       / 60,   1),
                "context_switches":  switches,
            },
            "top_apps": top_apps,
            "insights": self._get_insights(sessions),
        }

    def _get_insights(self, sessions: list) -> list:
        seen = set()
        insights = []

        for session in sessions:
            # start_time may be a datetime object (from aggregate) or an ISO string
            start = session["start_time"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace("Z", "+00:00"))
            hour = start.hour

            if "youtube" in session["app"].lower() and 9 <= hour <= 12:
                key = "Distraction during morning block"
                if key not in seen:
                    insights.append(key)
                    seen.add(key)

            if session["label"] == "focus" and session["duration_sec"] > 3600:
                key = "Achieved 1+ hour of deep focus"
                if key not in seen:
                    insights.append(key)
                    seen.add(key)

        return insights


# Module-level singleton
context_builder = ContextBuilder()