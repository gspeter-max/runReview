from app.agents.base import BaseAgent
from app.sdk.agent import AgentTask, AgentReport, Finding, Severity
from app.core.logging import logger
import asyncio

class MockSecurityAgent(BaseAgent):
    """Placeholder security agent for testing."""
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        logger.info("MockSecurityAgent starting", task_id=task.task_id)
        # Mock work
        await asyncio.sleep(0.1) 
        return AgentReport(
            agent_name="security",
            findings=[
                Finding(
                    title="Hardcoded Secrets",
                    severity=Severity.HIGH,
                    file_path=".env",
                    description="Detected potential API keys in plain text.",
                    suggestion="Use environment variables or a secret manager."
                )
            ],
            summary="Found critical vulnerabilities in auth logic."
        )

class MockQualityAgent(BaseAgent):
    """Placeholder quality agent for testing."""
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        logger.info("MockQualityAgent starting", task_id=task.task_id)
        # Mock work
        await asyncio.sleep(0.1)
        return AgentReport(
            agent_name="quality",
            findings=[
                Finding(
                    title="High Cyclomatic Complexity",
                    severity=Severity.MEDIUM,
                    file_path="app/main.py",
                    description="analyze_repo function is too complex.",
                    suggestion="Refactor logic into smaller helper functions."
                )
            ],
            summary="Code quality is acceptable but requires refactoring."
        )
