from app.agents.base import BaseAgent
from app.sdk.agent import AgentTask, AgentReport, Finding, Severity
from app.prompts.architecture import ARCHITECTURE_SYSTEM_PROMPT, build_architecture_prompt
from app.core.logging import logger
import json

class ArchitectureAgent(BaseAgent):
    """Specialized agent for architectural analysis."""
    
    async def execute(self, task: AgentTask, structure: str) -> AgentReport:
        """
        Analyze the structure provided in the task.
        In this implementation, structure is passed as repo_path context.
        """
        logger.info("ArchitectureAgent starting", task_id=task.task_id)
        prompt = build_architecture_prompt(structure)
        
        # In a real agent, we might want to return structured JSON as well.
        # For MVP, we'll wrap the text summary.
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
