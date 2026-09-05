from src.agents.base_agent import BaseSpecialistAgent

QUALITY_PROMPT = """You are a Code Quality & Logic Specialist. Analyze the provided git diff for correctness and logic bugs:
- Boundary condition errors & off-by-one bugs
- Null pointer / AttributeError / KeyError risks
- Unhandled exceptions or dead code
- Race conditions or resource leaks"""


class QualityAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(role="quality", system_prompt=QUALITY_PROMPT)
