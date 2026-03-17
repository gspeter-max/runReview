from abc import ABC, abstractmethod
from app.sdk.agent import AgentTask, AgentReport
from app.llmProvider.router import LLMRouter

class BaseAgent(ABC):
    """Abstract base class for all specialized subagents."""
    def __init__(self, provider: LLMRouter):
        self.provider = provider

    @abstractmethod
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        """Execute the agent's logic on the repository."""
        pass
