import asyncio
import hashlib
import hmac
import json
import os
import sys
from typing import Any, Dict, Tuple

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 stdout encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "testsecret")
os.environ["GITHUB_WEBHOOK_SECRET"] = SECRET
os.environ["GITHUB_TOKEN"] = os.getenv("GITHUB_TOKEN", "mock_token")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "mock_key")

WEBHOOK_URL = "http://127.0.0.1:8000/webhook"


def create_signed_payload(action: str = "opened", pr_number: int = 42, repo: str = "octocat/Hello-World") -> Tuple[bytes, Dict[str, str]]:
    """Generates a mock GitHub PR webhook JSON payload and returns (payload_bytes, headers)."""
    payload = {
        "action": action,
        "repository": {
            "full_name": repo,
            "html_url": f"https://github.com/{repo}",
        },
        "pull_request": {
            "number": pr_number,
            "title": "Add HMAC verification & 4 specialist review agents",
            "diff_url": f"https://github.com/{repo}/pull/{pr_number}.diff",
            "user": {"login": "octocat"},
        },
    }

    raw_bytes = json.dumps(payload, indent=2).encode("utf-8")

    # Compute HMAC SHA256 signature
    signature = "sha256=" + hmac.new(
        key=SECRET.encode("utf-8"),
        msg=raw_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "pull_request",
    }

    return raw_bytes, headers


def run_pipeline_tests():
    """Executes full multi-agent pipeline verification test."""
    from fastapi.testclient import TestClient
    from src.main import app, process_pr_review

    print("=== Testing FastAPI Webhook Server & Multi-Agent Endpoints ===")
    client = TestClient(app)

    # 1. Test /health
    health_res = client.get("/health")
    print(f"GET /health status: {health_res.status_code}, response: {health_res.json()}")
    assert health_res.status_code == 200

    # 2. Test Invalid Signature (401)
    raw_bytes, headers = create_signed_payload()
    invalid_headers = dict(headers, **{"X-Hub-Signature-256": "sha256=invalid"})
    bad_res = client.post("/webhook", content=raw_bytes, headers=invalid_headers)
    print(f"POST /webhook (invalid sig) status: {bad_res.status_code}, response: {bad_res.json()}")
    assert bad_res.status_code == 401

    # 3. Test Valid Signature (200)
    valid_res = client.post("/webhook", content=raw_bytes, headers=headers)
    print(f"POST /webhook (valid sig) status: {valid_res.status_code}, response: {valid_res.json()}")
    assert valid_res.status_code == 200

    # 4. Test Full Multi-Agent PR Review Pipeline Execution
    print("\n=== Executing Multi-Agent PR Review Pipeline (4 Specialist Passes) ===")
    pipeline_output = asyncio.run(
        process_pr_review(
            repo_full_name="octocat/Hello-World",
            pr_number=42,
            pr_diff_url="https://github.com/octocat/Hello-World/pull/42.diff"
        )
    )
    print(f"Pipeline Result Status: {pipeline_output['status']}")
    print(f"Files Parsed: {pipeline_output['parsed_files_count']}")
    print(f"Verdict Generated: {pipeline_output['verdict']}")
    print(f"Inline Comments Extracted: {pipeline_output['inline_comments_count']}")

    print("\n--- Review Summary Report ---")
    print(pipeline_output["body_summary"])

    print("\n--- Sample Extracted Inline Line-Level Comments ---")
    for idx, c in enumerate(pipeline_output["github_review_response"].get("inline_comments", []), start=1):
        print(f"\n[Inline Comment #{idx}] File: {c['path']} (Line {c['line']})")
        print(c["body"])

    print("\n[SUCCESS] MULTI-AGENT PR REVIEW PIPELINE VERIFIED SUCCESSFULLY!")


if __name__ == "__main__":
    run_pipeline_tests()
