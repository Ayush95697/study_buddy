import json
from datetime import datetime, timedelta
from collections import Counter


class ContextBuilder:
    def __init__(self, idle_threshold=120):
        self.idle_threshold = idle_threshold

    def build_summary(self, sessions, target_date):
        """
        Transforms raw session data into a privacy-safe JSON summary for the LLM.
        """
        if not sessions:
            return None

        # 1. Calculate Totals (Durations)
        totals = {
            "focus": 0,
            "distraction": 0,
            "away": 0,
            "neutral": 0
        }

        app_counts = Counter()
        longest_streak = 0
        current_streak = 0
        switches = 0
        prev_label = None

        for session in sessions:
            label = session['label']
            duration = session['duration_sec']

            # Add to totals
            if label in totals:
                totals[label] += duration

            # Track Apps (Privacy: Only keep the app name, not the window title)
            if label != 'away':
                app_counts[session['app']] += duration

            # Calculate Longest Focus Streak
            if label == 'focus':
                current_streak += duration
                if current_streak > longest_streak:
                    longest_streak = current_streak
            else:
                current_streak = 0

            # Count Context Switches
            if prev_label and label != prev_label:
                switches += 1
            prev_label = label

        # 2. Extract Top 3 Apps
        top_apps = [{"app": app, "time_min": round(sec / 60, 1)}
                    for app, sec in app_counts.most_common(3)]

        # 3. Detect Specific "Event" Insights
        insights = self._get_insights(sessions)

        # 4. Construct the Final JSON
        summary = {
            "date": target_date,
            "metrics": {
                "focus_hours": round(totals['focus'] / 3600, 2),
                "distraction_hours": round(totals['distraction'] / 3600, 2),
                "away_hours": round(totals['away'] / 3600, 2),
                "longest_streak_min": round(longest_streak / 60, 1),
                "context_switches": switches
            },
            "top_apps": top_apps,
            "insights": insights
        }

        return summary

    def _get_insights(self, sessions):
        """
        Detects patterns like 'YouTube during morning' or 'Late night coding'.
        """
        insights = []
        for session in sessions:
            start_hour = session['start_time'].hour

            # Example: YouTube during study hours (9 AM - 12 PM)
            if "youtube" in session['app'].lower() and 9 <= start_hour <= 12:
                if "Distraction during morning block" not in insights:
                    insights.append("Distraction during morning block")

            # Example: Deep work session
            if session['label'] == 'focus' and session['duration_sec'] > 3600:
                insights.append("Achieved 1+ hour of deep focus")

        return list(set(insights))  # Remove duplicates


# Helper instance
context_builder = ContextBuilder()