# Two main table
# One for raw data
# One for report

import sqlite3

# Table for raw data snapshots (Every 5 seconds)
CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,         -- ISO format (UTC)
    app TEXT NOT NULL,               -- e.g., 'chrome.exe'
    title TEXT,                      -- Window title
    idle_sec REAL DEFAULT 0,         -- Seconds since last input
    label TEXT                       -- focus, distraction, away, neutral
);
"""

# Table for merged sessions (Aggregated data)
CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_sec REAL,
    app TEXT,
    label TEXT
);
"""

# Table for the "WhatsApp-style" summaries
CREATE_REPORTS_TABLE = """
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day DATE UNIQUE NOT NULL,        -- Format: YYYY-MM-DD
    generated_text TEXT,             -- The "harsh" or "praising" message
    summary_json TEXT                -- JSON object for future UI charts
);
"""

def initialize_db(db_path="study_buddy.db"):
    """Creates the database and all tables if they don't exist."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(CREATE_EVENTS_TABLE)
            cursor.execute(CREATE_SESSIONS_TABLE)
            cursor.execute(CREATE_REPORTS_TABLE)
            conn.commit()
            print(f"Database initialized at {db_path}")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":

    initialize_db()