import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from src.api.health_router import router as health_router
from src.api.hitl_router import router as hitl_router
from src.auth.hmac_auth import verify_signature
from src.database.repository import EventRepository
from src.github_client import GitHubClient
from src.orchestrator.fan_out import orchestrate_multi_agent_review
from src.analyzer import parse_diff

load_dotenv()

app = FastAPI(title="Production AI PR Review Agent (23-Module Architecture)")

app.include_router(health_router)
app.include_router(hitl_router)


async def process_pr_review(repo_full_name: str, pr_number: int, pr_diff_url: str, event_id: Optional[int] = None) -> Dict[str, Any]:
    """
    23-Module Enterprise PR Review Pipeline:
    1. Downloads raw PR diff using GitHub API.
    2. Parses diff and filters out lockfiles/binaries.
    3. Runs 4 specialist reasoner agents (Security, Quality, Tests, Docs) with 3-Tier Memory (Semantic, Episodic, Procedural).
    4. Deduplicates findings and evaluates Human-in-the-Loop confidence gate.
    5. Posts inline review comments & summary report to GitHub.
    6. Logs execution trace and memory updates to data spine.
    """
    github_client = GitHubClient()

    # 1. Fetch Diff
    diff_text = await github_client.fetch_pr_diff(pr_diff_url)

    # 2. Parse & Filter Diff
    parsed_files = parse_diff(diff_text)

    # 3. Multi-Agent Orchestrator with 3-Tier Memory
    body_summary, inline_comments, verdict, passed_hitl = await orchestrate_multi_agent_review(
        parsed_files=parsed_files,
        repository=repo_full_name,
        pr_number=pr_number,
        event_id=event_id,
    )

    # 4. Submit PR Review to GitHub if passed HITL gate
    review_result = {}
    if passed_hitl:
        review_result = await github_client.post_pr_review(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            body_summary=body_summary,
            event=verdict if verdict in ["APPROVE", "REQUEST_CHANGES"] else "COMMENT",
            inline_comments=inline_comments,
        )

    # 5. Log Review to Event Spine Database
    if event_id:
        EventRepository.log_review(
            event_id=event_id,
            repository=repo_full_name,
            pr_number=pr_number,
            verdict=verdict,
            inline_comments_count=len(inline_comments),
            summary_md=body_summary,
        )

    return {
        "status": "completed",
        "event_id": event_id,
        "parsed_files_count": len(parsed_files),
        "verdict": verdict,
        "passed_hitl_gate": passed_hitl,
        "inline_comments_count": len(inline_comments),
        "body_summary": body_summary,
        "github_review_response": review_result,
    }


@app.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
):
    """
    Webhook ingress endpoint processing GitHub PR events.
    Verifies signature and triggers 23-module enterprise PR review pipeline in background.
    """
    raw_body = await request.body()

    if not verify_signature(raw_body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    if x_github_event and x_github_event != "pull_request":
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": f"Event '{x_github_event}' is not pull_request"},
        )

    try:
        payload: Dict[str, Any] = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    action = payload.get("action")
    if action not in ["opened", "synchronize"]:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ignored", "reason": f"Action '{action}' is ignored"},
        )

    repository = payload.get("repository", {}) if isinstance(payload.get("repository"), dict) else {}
    pull_request = payload.get("pull_request", {}) if isinstance(payload.get("pull_request"), dict) else {}

    repo_full_name = repository.get("full_name", "unknown/repo")
    pr_number = pull_request.get("number", 0)
    pr_diff_url = pull_request.get("diff_url", "")

    event_id = EventRepository.log_event(
        event_type="pull_request",
        repository=repo_full_name,
        pr_number=pr_number,
        action=action,
        status="received",
    )

    pr_metadata = {
        "event_id": event_id,
        "action": action,
        "repository_full_name": repo_full_name,
        "pull_request_number": pr_number,
        "pull_request_diff_url": pr_diff_url,
    }

    background_tasks.add_task(
        process_pr_review,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        pr_diff_url=pr_diff_url,
        event_id=event_id,
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "processed",
            "message": "Enterprise 23-module PR review pipeline triggered in background",
            "metadata": pr_metadata,
        },
    )