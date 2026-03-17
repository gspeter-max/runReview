from app.agents.base import BaseAgent
from app.sdk.agent import AgentTask, AgentReport, Finding
from app.prompts.quality import QUALITY_SYSTEM_PROMPT
import json

class QualityAgent(BaseAgent):
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        instruction = f"Task: {task.instruction}\nRelevant Context Files to check: {', '.join(task.context_files)}"
        
        raw_output = await self.run_agent_loop(
            system_prompt=QUALITY_SYSTEM_PROMPT,
            task_instruction=instruction,
            repo_path=repo_path,
            model_group=task.model_priority
        )
        
        try:
            json_str = raw_output.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            data = json.loads(json_str)
            findings = [Finding(**f) for f in data.get("findings", [])]
            return AgentReport(
                agent_name="quality",
                findings=findings,
                summary=data.get("summary", "No summary provided."),
                raw_output=raw_output
            )
        except Exception:
            return AgentReport(agent_name="quality", summary="Failed to parse quality findings", raw_output=raw_output)
