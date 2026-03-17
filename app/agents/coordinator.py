import json
from typing import List
from app.sdk.agent import AgentTask
from app.llmProvider.router import LLMRouter
from app.prompts.coordinator import COORDINATOR_SYSTEM_PROMPT, build_coordinator_prompt
from app.core.logging import logger

class Coordinator:
    """The Map-Reduce Planner: Analyzes task and generates a task list."""
    def __init__(self, provider: LLMRouter):
        self.provider = provider

    async def plan(self, structure: str, user_request: str = "Analyze this repository.") -> List[AgentTask]:
        """
        Takes repository structure and user request, returns list of tasks.
        """
        prompt = build_coordinator_prompt(structure, user_request)
        logger.info("Coordinator Planning", user_request=user_request)
        
        raw_response = await self.provider.generate(
            prompt=prompt,
            system_prompt=COORDINATOR_SYSTEM_PROMPT
        )
        
        try:
            # Basic JSON extraction in case of markdown blocks
            json_str = raw_response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3].strip()
            elif json_str.startswith("```"):
                json_str = json_str[3:-3].strip()
            
            tasks_data = json.loads(json_str)
            tasks = [AgentTask(**t) for t in tasks_data]
            logger.info("Coordinator plan generated", task_count=len(tasks))
            return tasks
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Coordinator failed to parse JSON", error=str(e), raw_output=raw_response)
            # Default fallback tasks if planner fails
            return [
                AgentTask(task_id="fallback-1", agent="architecture", instruction="Analyze overall structure."),
                AgentTask(task_id="fallback-2", agent="quality", instruction="Check for obvious quality issues.")
            ]
