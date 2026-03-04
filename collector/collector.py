from aw_core.models import Event
from datetime import datetime, timezone
import keyboard
from pycaw.pycaw import AudioUtilities
import win32api
from config import POLLING_INTERVAL, IDLE_THRESHOLD
import time
from win_active import get_active_window_info
from idle_time import get_idle_seconds



# Now we can use it immediately:
my_event = Event(timestamp=datetime.now(timezone.utc), data={"app": "terminal"})


def get_idle_time():
    """Returns the idle time in seconds."""
    # GetLastInputInfo returns the time of the last input event in milliseconds
    last_input_info = win32api.GetLastInputInfo()
    # GetTickCount returns the total time the system has been up in milliseconds
    current_tick = win32api.GetTickCount()

    idle_ms = current_tick - last_input_info
    return idle_ms / 1000.0
# to check if it is producing and audio
def is_audio_playing():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.State == 1:  # State 1 means 'Active/Playing'
            return True
    return False


if __name__ == "__main__":
    print(f"Study Buddy Collector is ACTIVE.")
    print(f"Settings: Poll every {POLLING_INTERVAL}s | Idle limit: {IDLE_THRESHOLD}s")
    print("Press CTRL+ALT+Q to stop safely.")

    try:
        while True:
            # 1. Global Kill Switch (Check before doing any work)
            if keyboard.is_pressed('ctrl+alt+q'):
                print("\nShutdown signal received. Closing collector...")
                break

            # 2. Collect Data from Sensors
            # From idle_time.py
            seconds_inactive = get_idle_seconds()

            # Local function in collector.py
            is_playing_audio = is_audio_playing()

            # From win_active.py
            app_name, window_title = get_active_window_info()

            # 3. Apply Activity Logic (The "Away" Rule)
            final_app = app_name
            final_title = window_title

            # Logic: If no movement AND no sound, you are Away.
            # If idle but sound is playing, we assume you are watching a tutorial.
            if seconds_inactive > IDLE_THRESHOLD:
                if not is_playing_audio:
                    final_app = "Away"
                    final_title = "User is Idle"
                else:
                    # Optional: Mark that you are passively watching
                    final_title = f"[Passive] {window_title}"

            # 4. Package as an ActivityWatch Event
            # Uses the Event class you pasted/imported earlier
            current_event = Event(
                timestamp=datetime.now(timezone.utc),
                data={
                    "app": final_app,
                    "title": final_title
                }
            )

            # 5. Output and Pause
            print(f"[{current_event.timestamp.strftime('%H:%M:%S')}] "
                  f"{final_app} | {final_title[:40]}... | Idle: {int(seconds_inactive)}s")

            # TODO: In the next step, we will add:
            # save_to_database(current_event)

            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\nManual stop detected. Exiting...")




