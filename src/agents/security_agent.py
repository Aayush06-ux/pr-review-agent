from src.agents.base_agent import BaseSpecialistAgent

SECURITY_PROMPT = """You are a Security Review Specialist. Analyze the provided git diff for security vulnerabilities:
- Injection risks (SQL, Command, OS)
- Hardcoded API keys, tokens, or secrets
- Unsafe input validation or missing authentication
- OWASP Top 10 vulnerabilities"""


class SecurityAgent(BaseSpecialistAgent):
    def __init__(self):
        super().__init__(role="security", system_prompt=SECURITY_PROMPT)
