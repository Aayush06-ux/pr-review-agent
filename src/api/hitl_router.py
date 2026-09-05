from fastapi import APIRouter
from src.database.db_engine import get_db_connection

router = APIRouter(prefix="/hitl", tags=["hitl"])


@router.get("/queue")
async def get_hitl_queue():
    """Retrieves pending reviews requiring Human-in-the-Loop approval."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hitl_approval_queue WHERE status = 'pending' ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]
