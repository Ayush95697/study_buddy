import win32api


def get_idle_seconds():
    """
    Detects how long the user has been inactive.
    Returns: idle_seconds (float)
    """
    try:
        # Get the time of the last input event in milliseconds
        last_input_ms = win32api.GetLastInputInfo()

        # Get the total time the system has been up in milliseconds
        current_tick_ms = win32api.GetTickCount()

        # Calculate the difference and convert to seconds
        idle_duration_ms = current_tick_ms - last_input_ms
        return idle_duration_ms / 1000.0

    except Exception:
        # Fallback if the API call fails
        return 0.0