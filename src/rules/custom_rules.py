import os
from typing import List
from src.memory.procedural import ProceduralMemory


class CustomRulesEngine:
    """Custom repository review rules engine."""

    def __init__(self, root_dir: str = None):
        self.procedural_memory = ProceduralMemory(root_dir)

    def get_active_rules(self) -> str:
        """Returns loaded repository coding standards and procedural rules."""
        return self.procedural_memory.get_procedural_guidelines()
