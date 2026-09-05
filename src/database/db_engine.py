import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "events_spine.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the local SQLite time-ordered event database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema for events, agent traces, reviews, and HITL approval queue."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Webhook Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                repository TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Specialist Agent Execution Traces Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                model TEXT NOT NULL,
                findings_count INTEGER NOT NULL,
                findings_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        # Published PR Reviews Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                repository TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                inline_comments_count INTEGER NOT NULL,
                summary_md TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        # HITL Approval Queue Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hitl_approval_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                repository TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                confidence_score REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                summary_md TEXT NOT NULL,
                inline_comments_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)
        conn.commit()


# Initialize schema on import
init_db()
