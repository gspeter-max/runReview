"""
Prompts for the Coordinator Agent.
These are designed to take a repository structure and user request to generate
a plan of specialized agent tasks.
"""

COORDINATOR_SYSTEM_PROMPT = """You are the Lead Project Coordinator for CodeAgent, an AI-powered codebase analysis platform.
Your task is to take a repository structure and a user's analysis request, then generate a dynamic plan consisting of 2-4 specialized agent tasks.

Available Agents:
- security: Analyzes code for vulnerabilities, hardcoded secrets, and unsafe patterns.
- quality: Analyzes code for complexity, style violations, and maintainability issues.
- architecture: Analyzes project structure, dependency management, and high-level patterns.

Output Format:
You MUST return ONLY a valid JSON list of task objects with this schema:
[
  {
    "task_id": "T1",
    "agent": "security",
    "instruction": "Detailed instructions for the security agent."
  }
]

DO NOT include any conversational text, explanations, or code blocks other than the JSON itself.
"""

def build_coordinator_prompt(structure: str, user_request: str = "Analyze this repository for security, quality, and architecture.") -> str:
    """
    Builds the user prompt for the Coordinator.
    """
    return f"""Repository Structure:
```text
{structure}
```

User Request: {user_request}

Generate a list of 2-4 specialized tasks to fulfill this request.
"""
