import sqlite3
from datetime import datetime
import os

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'study_buddy.db')


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        """Helper to create a connection with row factory for dictionary-like results."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def insert_event(self, event_obj, label="neutral"):
        """
        Takes an aw_core Event object and saves it to the database.
        """
        query = """
        INSERT INTO events (timestamp, app, title, idle_sec, label)
        VALUES (?, ?, ?, ?, ?)
        """
        # Extract data from the Event object

        timestamp_str = event_obj.timestamp.isoformat()
        app = event_obj.data.get("app", "Unknown")
        title = event_obj.data.get("title", "Unknown")
        # We calculate idle_sec elsewhere or pass it in; here we assume it's in data or passed
        idle_sec = event_obj.data.get("idle_sec", 0)

        try:
            with self._get_connection() as conn:
                conn.execute(query, (timestamp_str, app, title, idle_sec, label))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database Insert Error: {e}")

    def fetch_daily_events(self, target_date):
        """
        Fetches all events for a specific day (YYYY-MM-DD).
        """
        query = "SELECT * FROM events WHERE timestamp LIKE ? ORDER BY timestamp ASC"
        date_query = f"{target_date}%"

        try:
            with self._get_connection() as conn:
                rows = conn.execute(query, (date_query,)).fetchall()
                # Convert rows to list of dicts for easier processing in aggregate.py
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database Fetch Error: {e}")
            return []

    def store_report(self, day, text, summary_json):
        """Saves the final WhatsApp-style report."""
        query = """
        INSERT OR REPLACE INTO daily_reports (day, generated_text, summary_json)
        VALUES (?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                conn.execute(query, (day, text, summary_json))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database Report Error: {e}")


# Create a singleton instance for easy importing
db = DatabaseManager()