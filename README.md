# 🚀 Production-Grade AI PR Review Agent

An automated, multi-agent Pull Request review agent built with Python, FastAPI, and Groq LLMs (`qwen/qwen3.6-27b`), designed following the first-principles architecture from the Antern study (*Designing an AI Pull-Request Review Agent*).

---

## 🌟 Key Architecture & Features

- **🛡️ 4 Specialist Fan-Out Agents**: Runs concurrent reasoning passes across:
  1. **Security Specialist**: OWASP vulnerabilities, hardcoded secrets, injection vectors.
  2. **Code Quality & Logic Specialist**: Boundary bugs, null pointer hazards, unhandled exceptions.
  3. **Tests & Reliability Specialist**: Test coverage gaps and brittle assertions.
  4. **Docs Specialist**: Undocumented public APIs and missing docstrings.
- **📍 Inline Line-Level PR Review Comments**: Formats findings attached directly to exact lines in GitHub's PR diff UI (`POST /repos/{owner}/{repo}/pulls/{pr}/reviews`).
- **🔍 RAG Codebase Grounding**: Embedded local symbol & context indexer (`src/codebase_indexer.py`) providing codebase context to specialist agents beyond the diff lines.
- **⚡ Findings Aggregator & Deduplication**: Merges overlapping specialist findings, ranks severity, and generates an automated PR verdict (`APPROVE`, `COMMENT`, `REQUEST_CHANGES`).
- **📊 Time-Ordered Data Spine**: Embedded SQLite event log database (`data/events_spine.db`) tracking webhooks, specialist agent execution traces, and published reviews.
- **🌐 100% Free Live Tunnel**: Uses Cloudflare Tunnels (`cloudflared`) for permanent HTTPS webhook ingress with $0 cloud cost.
- **💻 CLI Local Runner**: Run AI code reviews directly on local git diffs offline from your terminal.

---

## 🛠️ Quick Start Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/pr-review-agent.git
cd pr-review-agent

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a `.env` file in the root directory:
```env
GITHUB_WEBHOOK_SECRET=my_super_secret_webhook_key
GITHUB_TOKEN=ghp_your_github_token_here
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 3. Run Tests
Execute the full multi-agent integration test suite:
```bash
.\venv\Scripts\python.exe tests/mock_webhook.py
```

### 4. Run Offline CLI Review
Run the reviewer locally on your local git diff:
```bash
.\venv\Scripts\python.exe -m src.cli
```

### 5. Launch Live Server & Cloudflare Tunnel
Start the FastAPI server and free Cloudflare tunnel in one command:
```bash
.\venv\Scripts\python.exe scripts/run_live_tunnel.py
```
Copy the generated `https://<subdomain>.trycloudflare.com/webhook` URL into your **GitHub Repository Settings -> Webhooks**!

---

## 📁 Repository Structure

```text
pr-review-agent/
├── src/
│   ├── main.py               # FastAPI Webhook Ingress & Pipeline Wiring
│   ├── analyzer.py           # Multi-Agent Specialist Reasoners
│   ├── aggregator.py         # Findings Deduplication & Ranking Engine
│   ├── codebase_indexer.py   # Codebase Context Indexer (RAG Grounding)
│   ├── db.py                 # Time-Ordered Event Log Spine (SQLite)
│   ├── github_client.py     # GitHub REST API & Review Comments Client
│   └── cli.py                # Offline CLI Local Review Runner
├── scripts/
│   └── run_live_tunnel.py    # 1-Click Server & Cloudflare Tunnel Launcher
├── tests/
│   └── mock_webhook.py       # Full Integration Test Suite
├── SPEC.md                   # System Design Specification
└── README.md                 # Project Documentation
```
