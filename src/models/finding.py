from typing import Optional
from pydantic import BaseModel
from src.models.enums import Severity


class Finding(BaseModel):
    """Pydantic model representing a single review finding from a specialist agent."""
    path: str
    line: int = 1
    severity: Severity = Severity.MEDIUM
    category: str
    title: str
    suggestion: str
    rationale: Optional[str] = None
    confidence: float = 1.0
