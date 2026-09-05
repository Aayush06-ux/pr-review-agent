import asyncio
from typing import Any, Dict, List, Optional, Tuple

from src.agents.security_agent import SecurityAgent
from src.agents.quality_agent import QualityAgent
from src.agents.test_agent import TestAgent
from src.agents.docs_agent import DocsAgent

from src.memory.semantic import SemanticMemory
from src.memory.episodic import EpisodicMemory
from src.memory.procedural import ProceduralMemory

from src.aggregator import format_review_payload
from src.hitl.confidence_gate import evaluate_confidence_gate


async def orchestrate_multi_agent_review(
    parsed_files: List[Dict[str, Any]],
    repository: str = "unknown/repo",
    pr_number: int = 0,
    event_id: Optional[int] = None
) -> Tuple[str, List[Dict[str, Any]], str, bool]:
    """
    Orchestrates the multi-agent PR review workflow:
    1. Loads 3-Tier Memory (Semantic, Episodic, Procedural).
    2. Runs 4 specialist agents concurrently using asyncio.gather.
    3. Merges and deduplicates findings via Aggregator.
    4. Evaluates Human-in-the-Loop (HITL) confidence gate.
    Returns: (summary_md, inline_comments, verdict, passed_hitl_gate)
    """
    files_to_review = [f for f in parsed_files if not f["is_ignored"]]
    ignored_files = [f for f in parsed_files if f["is_ignored"]]

    reviewed_names = [f["filename"] for f in files_to_review]
    ignored_names = [f["filename"] for f in ignored_files]

    if not files_to_review:
        summary, comments, verdict = format_review_payload([], reviewed_names, ignored_names)
        return summary, comments, verdict, True

    # 1. Load 3 Memory Systems
    semantic_mem = SemanticMemory()
    semantic_context = semantic_mem.get_semantic_context(reviewed_names)

    episodic_context = EpisodicMemory.get_episodic_context(repository, reviewed_names)

    procedural_mem = ProceduralMemory()
    procedural_context = procedural_mem.get_procedural_guidelines()

    # 2. Instantiate Specialist Agents
    security_agent = SecurityAgent()
    quality_agent = QualityAgent()
    test_agent = TestAgent()
    docs_agent = DocsAgent()

    # 3. Concurrent Fan-Out Execution
    results = await asyncio.gather(
        security_agent.execute_review(files_to_review, semantic_context, episodic_context, procedural_context, event_id),
        quality_agent.execute_review(files_to_review, semantic_context, episodic_context, procedural_context, event_id),
        test_agent.execute_review(files_to_review, semantic_context, episodic_context, procedural_context, event_id),
        docs_agent.execute_review(files_to_review, semantic_context, episodic_context, procedural_context, event_id),
    )

    all_findings = []
    for specialist_findings in results:
        all_findings.extend(specialist_findings)

    # 4. Aggregation & Deduplication
    summary_md, inline_comments, verdict = format_review_payload(all_findings, reviewed_names, ignored_names)

    # 5. HITL Confidence Gate Check
    passed_hitl, confidence, reason = evaluate_confidence_gate(
        findings=all_findings,
        event_id=event_id or 0,
        repository=repository,
        pr_number=pr_number,
        summary_md=summary_md,
        inline_comments=inline_comments,
    )

    return summary_md, inline_comments, verdict, passed_hitl
