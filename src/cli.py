import asyncio
import os
import subprocess
import sys
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analyzer import analyze_pr_diff_multi_agent, parse_diff

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def get_local_git_diff(target_range: Optional[str] = None) -> str:
    """Runs git diff command to capture local changes."""
    cmd = ["git", "diff"]
    if target_range:
        cmd.append(target_range)
    else:
        cmd.append("HEAD~1")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            return result.stdout
    except Exception:
        pass

    # Fallback git status/diff check
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception:
        return ""


async def run_cli_review(target_range: Optional[str] = None):
    """Executes multi-agent PR review locally from terminal."""
    print("=========================================================")
    print("  🚀 AI PR REVIEW AGENT (CLI Local Runner)")
    print("=========================================================")

    diff_text = get_local_git_diff(target_range)
    if not diff_text:
        print("No git diff detected. Making sample code review...")
        from src.github_client import GitHubClient
        diff_text = GitHubClient._get_mock_diff()

    parsed_files = parse_diff(diff_text)
    print(f"Parsed {len(parsed_files)} file patch(es)...")

    print("\nRunning 4 Specialist Agents (Security, Quality, Tests, Docs)...")
    summary_md, inline_comments, verdict = await analyze_pr_diff_multi_agent(parsed_files)

    print("\n=========================================================")
    print("  RESULTS & AUDIT REPORT")
    print("=========================================================")
    print(summary_md)

    print("\n---------------------------------------------------------")
    print(f"  INLINE COMMENTS ({len(inline_comments)}):")
    print("---------------------------------------------------------")
    for idx, c in enumerate(inline_comments, start=1):
        print(f"\n[{idx}] File: {c['path']} (Line {c['line']})")
        print(c["body"])

    print("\n=========================================================")
    print(f"  FINAL VERDICT: [{verdict}]")
    print("=========================================================\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_cli_review(target))
