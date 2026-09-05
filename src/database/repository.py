import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.database.db_engine import get_db_connection


class EventRepository:
    """Repository class for CRUD operations on the SQLite time-ordered event data spine."""

    @staticmethod
    def log_event(event_type: str, repository: str, pr_number: int, action: str, status: str = "received") -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO events (event_type, repository, pr_number, action, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (event_type, repository, pr_number, action, status, now),
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def log_agent_trace(event_id: int, role: str, model: str, findings: List[Dict[str, Any]]):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO agent_traces (event_id, role, model, findings_count, findings_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id, role, model, len(findings), json.dumps(findings), now),
            )
            conn.commit()

    @staticmethod
    def log_review(event_id: int, repository: str, pr_number: int, verdict: str, inline_comments_count: int, summary_md: str):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO reviews (event_id, repository, pr_number, verdict, inline_comments_count, summary_md, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (event_id, repository, pr_number, verdict, inline_comments_count, summary_md, now),
            )
            cursor.execute("UPDATE events SET status = 'completed' WHERE id = ?", (event_id,))
            conn.commit()

    @staticmethod
    def enqueue_hitl(event_id: int, repository: str, pr_number: int, confidence: float, summary_md: str, inline_comments: List[Dict[str, Any]]) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute(
                "INSERT INTO hitl_approval_queue (event_id, repository, pr_number, confidence_score, status, summary_md, inline_comments_json, created_at) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)",
                (event_id, repository, pr_number, confidence, summary_md, json.dumps(inline_comments), now),
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_recent_events(limit: int = 10) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
