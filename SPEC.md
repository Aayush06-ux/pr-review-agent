# AI PR Review Agent Specification

## 1. Project Overview
An automated Pull Request review agent that listens to GitHub PR webhooks, parses the code diff, analyzes the changes using specialized LLM reasoning prompts, and posts structured feedback back to the PR.

## 2. Tech Stack (100% Free)
- **Runtime:** Python 3.11+, FastAPI, Uvicorn
- **Tunneling (Local Demo):** Cloudflare Tunnels (`cloudflared`)
- **LLM Inference:** Groq API (`llama-3.3-70b-versatile`) or Google AI Studio (Gemini) using OpenAI-compatible SDK
- **Git Integration:** GitHub REST API & Webhooks (`X-Hub-Signature-256`)
- **Data Validation:** Pydantic v2

## 3. Architecture Pipeline
1. **Ingress:**
   - POST `/webhook` endpoint in FastAPI.
   - Verify HMAC SHA-256 signature using `GITHUB_WEBHOOK_SECRET`.
   - Filter events: process only `action` in `["opened", "synchronize"]`.

2. **Diff Fetching & Parsing:**
   - Extract repository name, PR number, and diff URL from webhook payload.
   - Fetch PR diff via GitHub API.
   - Parse diff into per-file patches and filter out lockfiles/binaries.

3. **Multi-Agent Reasoning:**
   - **Security Reviewer:** Detect vulnerabilities (injection, hardcoded secrets, unsafe calls).
   - **Logic & Edge Cases:** Detect bugs, unhandled nulls, boundary issues.
   - **Style & Clean Code:** Verify naming conventions, readability, maintainability.

4. **Output & Publication:**
   - Aggregate reviews into a structured markdown report.
   - Post comments back to the PR via GitHub REST API (`/repos/{owner}/{repo}/issues/{issue_number}/comments`).

## 4. Environment Variables Required (.env)
- `GITHUB_WEBHOOK_SECRET`: Secret key for HMAC verification
- `GITHUB_TOKEN`: Personal Access Token (classic or fine-grained) with `repo` scope
- `GROQ_API_KEY`: API key from console.groq.com