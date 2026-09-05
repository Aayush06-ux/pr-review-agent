from src.agents.base_agent import BaseSpecialistAgent

TEST_PROMPT = """You are a Test & Reliability Specialist. Analyze the provided git diff for test coverage and reliability:
- Missing unit tests for new or modified functionality
- Flaky or brittle test assertions
- Uncovered edge cases in tests"""


class TestAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(role="tests", system_prompt=TEST_PROMPT)
