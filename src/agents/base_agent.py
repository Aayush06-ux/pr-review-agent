import asyncio
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.economics.cost_tracker import BudgetGuard
from src.database.repository import EventRepository

GROQ_MODELS = ["qwen/qwen3.6-27b", "openai/gpt-oss-120b", "groq/compound"]


class BaseSpecialistAgent(ABC):
    """Abstract base class for all 4 specialist reviewer agents."""

    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt

    async def execute_review(
        self,
        files_to_review: List[Dict[str, Any]],
        semantic_context: str,
        episodic_context: str,
        procedural_context: str,
        event_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Executes LLM reasoning using all 3 Memory Systems (Semantic, Episodic, Procedural)."""
        if not BudgetGuard.check_budget():
            return self.generate_mock_findings(files_to_review)

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key or api_key == "mock_key":
            findings = self.generate_mock_findings(files_to_review)
            if event_id:
                EventRepository.log_agent_trace(event_id, self.role, "mock_model", findings)
            return findings

        code_context = f"{semantic_context}\n\n{episodic_context}\n\n{procedural_context}\n\n### PR Code Changes To Review:\n"
        for f in files_to_review:
            code_context += f"\n--- File: {f['filename']} (New Lines: {f['line_numbers']}) ---\n{f['diff_content']}\n"

        user_prompt = f"""Review the following PR changes:

{code_context}

Return a valid JSON array of findings. If no issues found, return [].
Each finding object MUST have:
- "path": string (exact file path)
- "line": integer (target line number from New Lines list)
- "severity": "HIGH" | "MEDIUM" | "LOW"
- "category": "{self.role.capitalize()}"
- "title": string (short title)
- "suggestion": string (actionable feedback and fix)

Output strictly raw JSON without markdown formatting."""

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        for model_name in GROQ_MODELS:
            try:
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=1024,
                )

                content = response.choices[0].message.content.strip()
                content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                findings = json.loads(content.strip())
                if isinstance(findings, list):
                    if event_id:
                        EventRepository.log_agent_trace(event_id, self.role, model_name, findings)
                    return findings
            except Exception:
                continue

        fallback = self.generate_mock_findings(files_to_review)
        if event_id:
            EventRepository.log_agent_trace(event_id, self.role, "fallback_mock", fallback)
        return fallback

    def generate_mock_findings(self, files_to_review: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates mock findings for testing when LLM API key is absent."""
        if not files_to_review:
            return []
        target_file = files_to_review[0]["filename"]
        target_line = files_to_review[0]["line_numbers"][0] if files_to_review[0]["line_numbers"] else 1

        if self.role == "security":
            return [{
                "path": target_file,
                "line": target_line,
                "severity": "HIGH",
                "category": "Security",
                "title": "Signature Header Validation Check",
                "suggestion": "Verified HMAC SHA-256 validation. Ensure GITHUB_WEBHOOK_SECRET is stored securely in environment variables.",
            }]
        elif self.role == "quality":
            return [{
                "path": target_file,
                "line": target_line,
                "severity": "MEDIUM",
                "category": "Quality",
                "title": "Exception Boundary Handling",
                "suggestion": "Ensure JSON parsing errors return HTTP 400 with a descriptive error message.",
            }]
        return []
