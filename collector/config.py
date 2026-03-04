# collector/config.py

# --- Time Settings ---
# How often the collector captures data (in seconds)
POLLING_INTERVAL = 5

# How long to wait before marking user as "Away" (in seconds)
IDLE_THRESHOLD = 120

# If two events are separated by more than this, they belong to different sessions
SESSION_GAP_THRESHOLD = 300  # 5 minutes

# --- Application Lists (Optional) ---
# You can use these later to auto-categorize your study time
STUDY_APPS = ["Code.exe", "pycharm64.exe", "cmd.exe", "python.exe"]
ENTERTAINMENT_APPS = ["vlc.exe", "Spotify.exe", "msedge.exe"]