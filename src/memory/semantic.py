import os
import re
from typing import Any, Dict, List, Set

EXCLUDE_DIRS = {".git", "venv", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"}
EXCLUDE_EXTS = {".png", ".jpg", ".pdf", ".zip", ".exe", ".dll", ".so", ".pyc", ".lock", ".json"}


class SemanticMemory:
    """
    Semantic Memory System (Codebase RAG Grounding).
    Indexes repository source files and symbol definitions (classes, functions, endpoints)
    to provide grounded codebase context to specialist LLM agents.
    """

    def __init__(self, root_dir: str = None):
        self.root_dir = root_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.symbol_index: Dict[str, Dict[str, Any]] = {}
        self.build_index()

    def build_index(self):
        """Scans workspace files and extracts symbol definitions."""
        self.symbol_index = {}
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTS or file.startswith("."):
                    continue

                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, self.root_dir).replace("\\", "/")

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    definitions = re.findall(r"^(?:async\s+)?(?:def|class)\s+([a-zA-Z0-9_]+)", content, flags=re.MULTILINE)
                    if definitions:
                        self.symbol_index[rel_path] = {
                            "symbols": definitions,
                            "snippet": content[:1500],
                        }
                except Exception:
                    continue

    def get_semantic_context(self, modified_files: List[str]) -> str:
        """Retrieves relevant symbol definitions and snippets for modified files."""
        context_snippets = []
        matched_files = set()

        for rel_path, data in self.symbol_index.items():
            if rel_path not in modified_files and rel_path not in matched_files:
                context_snippets.append(f"--- Semantic Context ({rel_path}) ---")
                context_snippets.append(data["snippet"][:500])
                matched_files.add(rel_path)
                if len(matched_files) >= 3:
                    break

        if not context_snippets:
            return "No additional semantic codebase context required."

        return "\n".join(context_snippets)
