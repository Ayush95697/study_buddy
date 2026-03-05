"""
core/db.py — Single database manager. Import the singleton `db` everywhere.
"""
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from core.schema import DB_PATH, initialize_db

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        # Ensure the database and tables exist before any operation.
        try:
            initialize_db(self.db_path)
        except Exception as e:
            logger.error("DB initialisation failed: %s", e)

    # ── Connection ────────────────────────────────────────────────────────────

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")   # Allow concurrent readers
        return conn

    # ── Generic helpers (used by memory_store etc.) ───────────────────────────

    def execute_custom(self, query, params=()):
        """Run an INSERT / UPDATE / DELETE and commit."""
        try:
            with self._get_conn() as conn:
                conn.execute(query, params)
                conn.commit()
        except sqlite3.Error as e:
            logger.error("DB execute error: %s", e)

    def fetch_custom(self, query, params=()):
        """Run a SELECT and return list-of-dicts."""
        try:
            with self._get_conn() as conn:
                rows = conn.execute(query, params).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.error("DB fetch error: %s", e)
            return []

    # ── Events ────────────────────────────────────────────────────────────────

    def insert_event(self, event_dict: dict, label: str = "neutral"):
        """
        Persist a raw activity sample.
        event_dict must have keys: timestamp (datetime or ISO str), app, title, idle_sec.
        """
        ts = event_dict.get("timestamp", datetime.now(timezone.utc))
        if isinstance(ts, datetime):
            ts = ts.isoformat()

        query = """
            INSERT INTO events (timestamp, app, title, idle_sec, label)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self._get_conn() as conn:
                conn.execute(query, (
                    ts,
                    event_dict.get("app", "Unknown"),
                    event_dict.get("title", ""),
                    event_dict.get("idle_sec", 0),
                    label,
                ))
                conn.commit()
        except sqlite3.Error as e:
            logger.error("DB insert_event error: %s", e)

    def fetch_daily_events(self, target_date: str):
        """
        Fetch all events for a local calendar date (YYYY-MM-DD).

        Events are stored as UTC ISO strings. We convert the local-date
        midnight boundaries to UTC so queries are timezone-correct even
        when local time != UTC (e.g. IST = UTC+5:30).
        """
        try:
            # Build local midnight and the next midnight in UTC
            local_tz = datetime.now().astimezone().tzinfo
            local_midnight = datetime.strptime(target_date, "%Y-%m-%d").replace(
                tzinfo=local_tz
            )
            utc_start = local_midnight.astimezone(timezone.utc).isoformat()
            utc_end = (local_midnight + timedelta(days=1)).astimezone(
                timezone.utc
            ).isoformat()

            query = """
                SELECT * FROM events
                WHERE timestamp >= ? AND timestamp < ?
                ORDER BY timestamp ASC
            """
            return self.fetch_custom(query, (utc_start, utc_end))
        except Exception as e:
            logger.error("fetch_daily_events error: %s", e)
            return []

    # ── Reports ───────────────────────────────────────────────────────────────

    def store_report(self, day: str, text: str, summary_json: str):
        """Upsert a daily LLM report (day = YYYY-MM-DD local date)."""
        query = """
            INSERT OR REPLACE INTO daily_reports (day, generated_text, summary_json)
            VALUES (?, ?, ?)
        """
        self.execute_custom(query, (day, text, summary_json))

    def fetch_report(self, day: str):
        """Return cached report for a day, or None."""
        rows = self.fetch_custom(
            "SELECT * FROM daily_reports WHERE day = ?", (day,)
        )
        return rows[0] if rows else None

    # ── User settings ─────────────────────────────────────────────────────────

    def update_user_setting(self, chat_id, key: str, value):
        """Upsert a user-specific setting."""
        query = """
            INSERT INTO user_settings (chat_id, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, key) DO UPDATE SET value=excluded.value
        """
        self.execute_custom(query, (str(chat_id), key, str(value)))

    def get_user_setting(self, chat_id, key: str, default=None):
        rows = self.fetch_custom(
            "SELECT value FROM user_settings WHERE chat_id=? AND key=?",
            (str(chat_id), key),
        )
        return rows[0]["value"] if rows else default


# Singleton — import this everywhere
db = DatabaseManager()