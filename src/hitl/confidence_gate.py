from typing import Any, Dict, List, Tuple
from src.database.repository import EventRepository


def evaluate_confidence_gate(
    findings: List[Dict[str, Any]],
    event_id: int,
    repository: str,
    pr_number: int,
    summary_md: str,
    inline_comments: List[Dict[str, Any]],
    confidence_threshold: float = 0.75
) -> Tuple[bool, float, str]:
    """
    Evaluates the Human-in-the-Loop (HITL) confidence gate (Section 0.3 & 3.4).
    If confidence < 0.75 or critical unverified findings exist, routes to human approval queue.
    Returns: (can_autopost: bool, confidence_score: float, reason: str)
    """
    if not findings:
        return True, 1.0, "Clean diff with no findings; approved for auto-posting."

    total_confidence = sum(f.get("confidence", 1.0) for f in findings)
    avg_confidence = total_confidence / len(findings)

    critical_count = sum(1 for f in findings if f.get("severity", "").upper() == "CRITICAL")

    if critical_count > 0 or avg_confidence < confidence_threshold:
        hitl_id = EventRepository.enqueue_hitl(
            event_id=event_id or 0,
            repository=repository,
            pr_number=pr_number,
            confidence=avg_confidence,
            summary_md=summary_md,
            inline_comments=inline_comments,
        )
        return False, avg_confidence, f"Low confidence ({avg_confidence:.2f}) or CRITICAL issue detected. Routed to HITL queue #{hitl_id}."

    return True, avg_confidence, "High confidence; passed HITL gate."
