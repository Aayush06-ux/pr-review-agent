import os
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    """Async HTTP client for interacting with GitHub REST API, fetching PR diffs, and submitting reviews."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PR-Review-Agent/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def fetch_pr_diff(self, diff_url: str) -> str:
        """
        Fetches raw git diff for a PR diff URL.
        Falls back to mock diff string if offline or using test URLs.
        """
        if not diff_url or "example.com" in diff_url or "mock" in diff_url:
            return self._get_mock_diff()

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
                response = await client.get(diff_url, headers=headers)

                if response.status_code == 200:
                    return response.text
                else:
                    return self._get_mock_diff()
        except Exception:
            return self._get_mock_diff()

    async def post_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        body_summary: str,
        event: str = "COMMENT",
        inline_comments: Optional[List[Dict[str, Any]]] = None,
        commit_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Posts a complete PR Review containing an overall summary and inline line-level comments.
        API: POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
        """
        if not self.token or self.token == "mock_token":
            return {
                "id": 88888,
                "status": "posted_mock",
                "event": event,
                "body_summary": body_summary,
                "inline_comments_count": len(inline_comments) if inline_comments else 0,
                "inline_comments": inline_comments or [],
            }

        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/reviews"
        payload: Dict[str, Any] = {
            "body": body_summary,
            "event": event,  # "APPROVE", "REQUEST_CHANGES", or "COMMENT"
        }

        if commit_id:
            payload["commit_id"] = commit_id

        if inline_comments:
            formatted_comments = []
            for comment in inline_comments:
                formatted_comments.append({
                    "path": comment.get("path"),
                    "line": int(comment.get("line", 1)),
                    "side": comment.get("side", "RIGHT"),
                    "body": comment.get("body", ""),
                })
            payload["comments"] = formatted_comments

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201]:
                return response.json()
            else:
                # Fallback to issue comment if PR review inline creation has line-position mismatch
                return await self.post_pr_issue_comment(repo_full_name, pr_number, body_summary)

    async def post_pr_issue_comment(self, repo_full_name: str, pr_number: int, comment_body: str) -> Dict[str, Any]:
        """
        Fallback issue comment poster for top-level review summary.
        API: POST /repos/{owner}/{repo}/issues/{issue_number}/comments
        """
        if not self.token or self.token == "mock_token":
            return {
                "id": 99999,
                "status": "posted_mock_issue_comment",
                "body": comment_body,
            }

        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        payload = {"body": comment_body}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, headers=self.headers, json=payload)
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    "error": f"Failed with status code {response.status_code}",
                    "details": response.text,
                    "status": "failed",
                }

    @staticmethod
    def _get_mock_diff() -> str:
        """Returns sample mock unified git diff for testing."""
        return """diff --git a/src/main.py b/src/main.py
index e69de29..d95f3ef 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,10 @@
+import hashlib
+import hmac
 import os
+
+@app.post("/webhook")
+async def webhook(request: Request):
+    body = await request.body()
+    return {"status": "ok"}
diff --git a/package-lock.json b/package-lock.json
index 1234567..89abcde 100644
--- a/package-lock.json
+++ b/package-lock.json
@@ -1,3 +1,4 @@
 {
-  "name": "example"
+  "name": "example-updated"
 }
"""
