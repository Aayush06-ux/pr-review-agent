import os
from typing import Dict


class BudgetGuard:
    """
    Economics & Cost Control Module (Phase 16 / ADR-004).
    Tracks token spend and enforces daily budget caps.
    """
    DAILY_BUDGET_CAP_USD = float(os.getenv("DAILY_BUDGET_CAP_USD", "10.0"))
    current_daily_spend_usd = 0.0

    @classmethod
    def check_budget(cls) -> bool:
        """Returns True if within budget limits."""
        return cls.current_daily_spend_usd < cls.DAILY_BUDGET_CAP_USD

    @classmethod
    def track_usage(cls, model: str, prompt_tokens: int, completion_tokens: int):
        """Calculates token costs for models and updates running daily total."""
        # Cost estimates per 1k tokens (Groq models are 100% free, so cost = $0.00)
        cost_per_1k_prompt = 0.0
        cost_per_1k_completion = 0.0

        if "gpt-4" in model:
            cost_per_1k_prompt = 0.03
            cost_per_1k_completion = 0.06

        cost = ((prompt_tokens / 1000.0) * cost_per_1k_prompt) + ((completion_tokens / 1000.0) * cost_per_1k_completion)
        cls.current_daily_spend_usd += cost
        return cost
