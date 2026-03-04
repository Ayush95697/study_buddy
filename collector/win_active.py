import pygetwindow as gw
import win32process
import psutil


def get_active_window_info():
    """
    Extracts foreground window details.
    Returns: (app_name, window_title)
    """
    try:
        active_win = gw.getActiveWindow()

        # If no window is focused (e.g., clicking the taskbar)
        if active_win is None:
            return "None", "None"

        window_title = active_win.title
        hwnd = active_win._hWnd

        # Linking the Window Handle to a Process Name
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        app_name = psutil.Process(pid).name()

        return app_name, window_title

    except (psutil.NoSuchProcess, Exception):
        # Fallback if the process closes during the check
        return "Unknown", "Unknown"