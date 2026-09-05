import sqlite3
from typing import Any, Dict, List, Optional
from src.database.db_engine import get_db_connection


class EpisodicMemory:
    """
    Episodic Memory System.
    Stores and retrieves past PR reviews, recurring findings, and resolution histories
    for modified repository files so agents learn from historical PR reviews.
    """

    @staticmethod
    def get_episodic_context(repository: str, modified_files: List[str]) -> str:
        """Retrieves past PR review histories and recurring findings for target repository & files."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT pr_number, verdict, summary_md, created_at FROM reviews WHERE repository = ? ORDER BY id DESC LIMIT 3",
                    (repository,),
                )
                rows = cursor.fetchall()

                if not rows:
                    return "No prior PR review history found for this repository."

                history_str = "### Episodic Memory (Past PR Review History):\n"
                for row in rows:
                    history_str += f"- PR #{row['pr_number']} (Verdict: {row['verdict']}, Date: {row['created_at'][:10]}):\n"
                    # Include first 2 lines of past review summary
                    summary_lines = row['summary_md'].splitlines()[:3]
                    history_str += "  " + "\n  ".join(summary_lines) + "\n"

                return history_str
        except Exception:
            return "Episodic memory unavailable."
