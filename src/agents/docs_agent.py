from src.agents.base_agent import BaseSpecialistAgent

DOCS_PROMPT = """You are a Documentation & Maintainability Specialist. Analyze the provided git diff for clarity:
- Undocumented public functions, endpoints, or classes
- Outdated or misleading code comments
- Complex logic lacking docstrings"""


class DocsAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(role="docs", system_prompt=DOCS_PROMPT)
