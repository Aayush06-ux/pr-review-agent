from typing import Any, Dict, List, Tuple


def deduplicate_and_rank_findings(raw_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicates overlapping findings on the same file path and line number,
    ranking them by severity (HIGH -> MEDIUM -> LOW).
    """
    seen_keys = set()
    deduped = []

    # Severity priority order
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

    # Sort raw findings by severity first
    sorted_raw = sorted(
        raw_findings,
        key=lambda f: severity_order.get(f.get("severity", "INFO").upper(), 4)
    )

    for f in sorted_raw:
        path = f.get("path", "unknown")
        line = f.get("line", 1)
        category = f.get("category", "General")

        # Key for deduplication: same file, same line, same category
        dedup_key = f"{path}:{line}:{category}"
        if dedup_key not in seen_keys:
            seen_keys.add(dedup_key)
            deduped.append(f)

    return deduped


def format_review_payload(
    all_findings: List[Dict[str, Any]],
    reviewed_files: List[str],
    ignored_files: List[str]
) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Aggregates specialist findings, calculates PR verdict, and builds inline comments + summary markdown.
    """
    findings = deduplicate_and_rank_findings(all_findings)

    # Determine Verdict
    high_count = sum(1 for f in findings if f.get("severity", "").upper() in ["CRITICAL", "HIGH"])
    medium_count = sum(1 for f in findings if f.get("severity", "").upper() == "MEDIUM")
    low_count = sum(1 for f in findings if f.get("severity", "").upper() in ["LOW", "INFO"])

    if high_count > 0:
        verdict = "REQUEST_CHANGES"
    elif medium_count > 0 or low_count > 0:
        verdict = "COMMENT"
    else:
        verdict = "APPROVE"

    # Build Inline GitHub Comments
    inline_comments = []
    for f in findings:
        category = f.get("category", "Review")
        icon = "🛡️" if category == "Security" else "🐛" if category == "Quality" else "🧪" if category == "Tests" else "📝"
        severity = f.get("severity", "INFO").upper()

        body = (
            f"### {icon} [{severity}] {f.get('title', 'Finding')}\n\n"
            f"**Category:** {category}\n"
            f"**Suggestion:** {f.get('suggestion', '')}"
        )

        inline_comments.append({
            "path": f.get("path"),
            "line": int(f.get("line", 1)),
            "side": "RIGHT",
            "body": body,
        })

    # Build Summary Markdown Report
    reviewed_str = ", ".join([f"`{name}`" for name in reviewed_files]) if reviewed_files else "None"
    ignored_str = ", ".join([f"`{name}`" for name in ignored_files]) if ignored_files else "None"

    summary_md = (
        "## AI PR Review Report\n\n"
        f"**Reviewed Files:** {reviewed_str}\n"
        f"**Ignored Files (Lockfiles/Binaries):** {ignored_str}\n\n"
        f"### 📊 Multi-Agent Audit Summary\n"
        f"- 🛡️ **Critical / High Severity:** `{high_count}`\n"
        f"- 🐛 **Medium Severity:** `{medium_count}`\n"
        f"- 📝 **Low Severity / Suggestions:** `{low_count}`\n"
        f"- 📌 **Total Inline Comments Posted:** `{len(inline_comments)}`\n\n"
        f"### 📝 Final Verdict\n"
    )

    if verdict == "REQUEST_CHANGES":
        summary_md += "- **REQUEST_CHANGES**: High severity issues detected. Please review inline comments before merging."
    elif verdict == "COMMENT":
        summary_md += "- **COMMENT**: Code is functional with minor suggestions posted inline."
    else:
        summary_md += "- **APPROVE**: Code is secure, well-structured, and ready to merge! 🎉"

    return summary_md, inline_comments, verdict
