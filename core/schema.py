"""
core/schema.py — Database table definitions and initializer.
Run directly to (re)create all tables: python core/schema.py
"""
import sqlite3
import os

# Canonical DB path — always relative to this file's directory (core/)
DB_PATH = os.path.join(os.path.dirname(__file__), "study_buddy.db")

# ── Raw event snapshots (every N seconds from collector) ─────────────────────
CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,   -- ISO-8601 UTC  e.g. 2026-03-05T10:00:00+00:00
    app         TEXT    NOT NULL,   -- Process name  e.g. 'Code.exe'
    title       TEXT,               -- Sanitised window title
    idle_sec    REAL    DEFAULT 0,  -- Seconds since last keyboard/mouse input
    label       TEXT                -- focus | distraction | neutral | away
);
"""

# ── Aggregated sessions (merged from consecutive same-label events) ───────────
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time   TEXT    NOT NULL,
    end_time     TEXT    NOT NULL,
    duration_sec REAL,
    app          TEXT,
    label        TEXT
);
"""

# ── Daily/Weekly LLM-generated reports ───────────────────────────────────────
CREATE_REPORTS_TABLE = """
CREATE TABLE IF NOT EXISTS daily_reports (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    day            DATE    UNIQUE NOT NULL,  -- YYYY-MM-DD  (local date)
    generated_text TEXT,                    -- Telegram-style message
    summary_json   TEXT                     -- Structured JSON for charts
);
"""

# ── Telegram conversation history (for chat memory) ──────────────────────────
CREATE_CHAT_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS chat_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id   TEXT    NOT NULL,
    role      TEXT    NOT NULL,   -- 'user' or 'assistant'
    text      TEXT    NOT NULL,
    timestamp TEXT    NOT NULL
);
"""

# ── Per-user settings (goals, strict-mode flag, etc.) ────────────────────────
CREATE_USER_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS user_settings (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT    NOT NULL,
    key     TEXT    NOT NULL,
    value   TEXT,
    UNIQUE(chat_id, key)
);
"""


def initialize_db(db_path=DB_PATH):
    """Creates the database and all tables if they don't exist."""
    try:
        with sqlite3.connect(db_path) as conn:
            for ddl in [
                CREATE_EVENTS_TABLE,
                CREATE_SESSIONS_TABLE,
                CREATE_REPORTS_TABLE,
                CREATE_CHAT_HISTORY_TABLE,
                CREATE_USER_SETTINGS_TABLE,
            ]:
                conn.execute(ddl)
            conn.commit()
        print(f"Database initialised at: {db_path}")
    except sqlite3.Error as e:
        print(f"Error initialising database: {e}")
        raise


if __name__ == "__main__":
    initialize_db()