from app.agents.base import BaseAgent
from app.sdk.agent import AgentTask, AgentReport, Finding, Severity
from app.prompts.architecture import ARCHITECTURE_SYSTEM_PROMPT, build_architecture_prompt
from app.core.logging import logger
import json

class ArchitectureAgent(BaseAgent):
    """Specialized agent for architectural analysis."""
    
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        """
        Analyze the repository structure for architectural patterns.
        """
        logger.info("ArchitectureAgent starting", task_id=task.task_id)
        
        # BOX vs GIFT fix: Get real file structure instead of raw path
        structure = self.repo_service.get_file_structure(repo_path, max_depth=4)
        prompt = build_architecture_prompt(structure)
        
        # In a real agent, we might want to return structured JSON as well.
        raw_summary = await self.provider.generate(
            prompt=prompt, 
            system_prompt=ARCHITECTURE_SYSTEM_PROMPT
        )
        
        # Simple extraction logic for demonstration
        findings = [
            Finding(
                title="Monolithic Structure",
                severity=Severity.MEDIUM,
                file_path="root",
                description="The project lacks clear separation of concerns in its current layout.",
                suggestion="Consider adopting a layered or hexagonal architecture."
            )
        ] if "monolith" in raw_summary.lower() else []

        return AgentReport(
            agent_name="architecture",
            findings=findings,
            summary=raw_summary
        )
