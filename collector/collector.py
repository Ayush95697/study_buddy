"""
collector/collector.py — Main data collection loop.
Do NOT run this directly; use `python run_collector.py` from the project root.
"""
import time
import logging
from datetime import datetime, timezone

from collector.config import POLLING_INTERVAL, IDLE_THRESHOLD
from collector.win_active import get_active_window_info
from collector.idle_time import get_idle_seconds
from core.db import db
from core.rules import label_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [COLLECTOR] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_collector():
    logger.info("Study Buddy Collector started.")
    logger.info("Poll every %ds | Idle cutoff: %ds | Press Ctrl+C to stop.", POLLING_INTERVAL, IDLE_THRESHOLD)

    while True:
        try:
            _collect_one_sample()
        except KeyboardInterrupt:
            logger.info("Collector stopped by user.")
            break
        except Exception as e:
            # Log but never crash — just wait and try again
            logger.error("Unexpected error in collect loop: %s", e)

        time.sleep(POLLING_INTERVAL)


def _collect_one_sample():
    """Capture one snapshot and write it to the database."""
    # 1. Sensors
    idle_sec = get_idle_seconds()
    app_name, window_title = get_active_window_info()

    # 2. Sanitise / privacy — strip title if app is Away
    if idle_sec > IDLE_THRESHOLD:
        app_name = "Away"
        window_title = "User is idle"

    # 3. Classify
    label = label_event(app_name, window_title, idle_sec, IDLE_THRESHOLD)

    # 4. Build event dict
    event = {
        "timestamp": datetime.now(timezone.utc),
        "app": app_name,
        "title": window_title[:120],   # cap title length stored in DB
        "idle_sec": round(idle_sec, 1),
    }

    # 5. Persist
    db.insert_event(event, label)

    logger.info("%-20s | %-8s | idle=%ds", app_name[:20], label, int(idle_sec))
