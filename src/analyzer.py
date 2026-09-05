import re
from typing import Any, Dict, List, Tuple

from src.orchestrator.fan_out import orchestrate_multi_agent_review

IGNORED_PATTERNS = [
    r"package-lock\.json$",
    r"yarn\.lock$",
    r"pnpm-lock\.yaml$",
    r"poetry\.lock$",
    r"Cargo\.lock$",
    r"Pipfile\.lock$",
    r"composer\.lock$",
    r"go\.sum$",
    r"Gemfile\.lock$",
    r"\.(png|jpg|jpeg|gif|ico|pdf|zip|gz|tar|exe|dll|so|dylib|woff|woff2|ttf|eot|pyc|svg|mp4|webp)$",
    r"\.min\.(js|css)$",
    r"\.map$",
]


def is_file_ignored(filename: str) -> bool:
    """Checks if a file should be ignored from code review (e.g. lockfiles, binaries, minified files)."""
    clean_filename = filename.strip()
    for pattern in IGNORED_PATTERNS:
        if re.search(pattern, clean_filename, re.IGNORECASE):
            return True
    return False


def parse_diff(diff_text: str) -> List[Dict[str, Any]]:
    """Parses a unified git diff string into structured file patches with line mappings."""
    if not diff_text or not diff_text.strip():
        return []

    parsed_files = []
    raw_patches = re.split(r"^diff --git ", diff_text, flags=re.MULTILINE)

    for patch in raw_patches:
        if not patch.strip():
            continue

        lines = patch.splitlines()
        first_line = lines[0]

        match = re.search(r"a/(.*?)\s+b/(.*)", first_line)
        if match:
            filename = match.group(2)
        else:
            filename_match = re.search(r"b/(\S+)", first_line)
            filename = filename_match.group(1) if filename_match else "unknown"

        ignored = is_file_ignored(filename)

        new_line_numbers = []
        current_new_line = 0
        for line in lines:
            hunk_match = re.match(r"^@@ -\d+,\d+ \+(\d+),?\d* @@", line)
            if hunk_match:
                current_new_line = int(hunk_match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                new_line_numbers.append(current_new_line)
                current_new_line += 1
            elif not line.startswith("-"):
                current_new_line += 1

        parsed_files.append({
            "filename": filename,
            "is_ignored": ignored,
            "diff_content": patch,
            "line_numbers": new_line_numbers or [1],
        })

    return parsed_files


async def analyze_pr_diff_multi_agent(
    parsed_files: List[Dict[str, Any]],
    repository: str = "unknown/repo",
    pr_number: int = 0,
    event_id: Any = None
) -> Tuple[str, List[Dict[str, Any]], str]:
    """Delegates PR diff analysis to the Multi-Agent Orchestrator with 3-Tier Memory."""
    summary_md, inline_comments, verdict, _ = await orchestrate_multi_agent_review(
        parsed_files=parsed_files,
        repository=repository,
        pr_number=pr_number,
        event_id=event_id,
    )
    return summary_md, inline_comments, verdict
