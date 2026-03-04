# core/rules.py

def label_event(app, title, idle_sec, idle_threshold=120):
    """
    Categorizes a raw event based on app name, window title, and inactivity.
    Returns: 'focus', 'distraction', 'neutral', or 'away'
    """

    # 1. Check for inactivity first (Highest Priority)
    if idle_sec > idle_threshold:
        return "away"

    # Normalize strings for easier matching
    app = app.lower()
    title = title.lower()

    # 2. Define Category Keywords
    # Tailored to your interests in AI, ML, and Web Dev
    FOCUS_APPS = [
        "code.exe", "visual studio code", "pycharm", "cursor.exe",
        "cmd.exe", "powershell.exe", "windows terminal", "python.exe"
    ]

    FOCUS_TITLES = [
        "leetcode", "github", "stack overflow", "chatgpt", "gemini",
        "documentation", "localhost", "jupyter", "colab"
    ]

    DISTRACTION_APPS = [
        "netflix.exe", "discord.exe", "steam.exe"
    ]

    DISTRACTION_TITLES = [
        "youtube", "facebook", "instagram", "twitter", "reddit"
    ]

    # 3. Apply Classification Logic
    # Check for Focus
    if any(f_app in app for f_app in FOCUS_APPS):
        return "focus"
    if any(f_title in title for f_title in FOCUS_TITLES):
        return "focus"

    # Check for Distraction
    if any(d_app in app for d_app in DISTRACTION_APPS):
        return "distraction"
    if any(d_title in title for d_title in DISTRACTION_TITLES):
        return "distraction"

    # Default if no rules match
    return "neutral"


if __name__ == "__main__":
    # Quick Test
    print(f"Testing VS Code: {label_event('Code.exe', 'main.py - Study_buddy', 0)}")
    print(f"Testing YouTube: {label_event('msedge.exe', 'Lo-fi Beats - YouTube', 0)}")
    print(f"Testing Inactivity: {label_event('Code.exe', 'main.py', 300)}")