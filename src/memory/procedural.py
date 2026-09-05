import os
from typing import Optional


class ProceduralMemory:
    """
    Procedural Memory System.
    Loads repository-specific guidelines, team review standards (.github/REVIEW_GUIDELINES.md or .pr-rules.json),
    and procedural rules to inject into specialist agent prompts.
    """

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def get_procedural_guidelines(self) -> str:
        """Loads repository-specific team review guidelines if present."""
        possible_paths = [
            os.path.join(self.root_dir, ".github", "REVIEW_GUIDELINES.md"),
            os.path.join(self.root_dir, ".github", "PULL_REQUEST_TEMPLATE.md"),
            os.path.join(self.root_dir, ".pr-rules.json"),
            os.path.join(self.root_dir, "SPEC.md"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    return f"### Procedural Memory (Team Review Guidelines from {os.path.basename(path)}):\n{content[:1000]}"
                except Exception:
                    continue

        return "Standard procedural guidelines: Ensure type hints, error handling, security validation, and test coverage."
