import asyncio
from typing import List, Dict, Type
from app.sdk.agent import AgentTask, AgentReport
from app.agents.base import BaseAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.agents.security_agent import SecurityAgent
from app.agents.quality_agent import QualityAgent
from app.llmProvider.router import LLMRouter
from app.core.logging import logger

AGENT_REGISTRY: Dict[str, Type[BaseAgent]] = {
    "security": SecurityAgent,
    "quality": QualityAgent,
    "architecture": ArchitectureAgent
}

class Orchestrator:
    """The Parallel Spawner: Orchestrates execution across multiple subagents."""
    def __init__(self, provider: LLMRouter):
        self.provider = provider

    async def spawn_agents(self, tasks: List[AgentTask], repo_path: str) -> List[AgentReport]:
        """
        Launches all subagents in parallel using asyncio.
        """
        logger.info("Spawning agents", task_count=len(tasks))
        
        spawned_tasks = []
        for task in tasks:
            agent_cls = AGENT_REGISTRY.get(task.agent)
            if agent_cls:
                agent_instance = agent_cls(self.provider)
                spawned_tasks.append(agent_instance.execute(task, repo_path))
            else:
                logger.warning("Agent not found in registry", agent_name=task.agent)

        if not spawned_tasks:
            return []

        # Run all tasks in parallel
        results = await asyncio.gather(*spawned_tasks, return_exceptions=True)
        
        final_reports = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error("Agent crashed", index=i, error=str(res))
                # Generate a graceful error report
                final_reports.append(AgentReport(
                    agent_name=tasks[i].agent,
                    summary=f"Error: Agent execution failed - {str(res)}",
                    findings=[]
                ))
            else:
                final_reports.append(res)
        
        return final_reports
