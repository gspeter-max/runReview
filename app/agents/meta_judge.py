import json
from typing import List, Dict, Any
from app.sdk.agent import AgentReport, Finding
from app.llmProvider.router import LLMRouter
from app.prompts.meta_judge import META_JUDGE_SYSTEM_PROMPT, build_meta_judge_prompt
from app.core.logging import logger

class MetaJudge:
    """The Meta-Judge (Reduce): Result Aggregator and Score Calculator."""
    def __init__(self, provider: LLMRouter):
        self.provider = provider

    async def judge(self, reports: List[AgentReport]) -> Dict[str, Any]:
        """
        Aggregates all agent findings and generates an executive summary.
        """
        logger.info("Meta-Judge starting judgment pass", agent_count=len(reports))
        
        # Flatten findings
        all_findings = []
        for r in reports:
            all_findings.extend(r.findings)
        
        # Prepare text reports for the LLM
        reports_text = "\n---\n".join([
            f"Agent: {r.agent_name}\nSummary: {r.summary}\nFindings: {len(r.findings)}"
            for r in reports
        ])
        
        prompt = build_meta_judge_prompt(reports_text)
        raw_response = await self.provider.generate(
            prompt=prompt,
            system_prompt=META_JUDGE_SYSTEM_PROMPT
        )

        try:
            # Extract JSON
            json_str = raw_response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:-3].strip()
            elif json_str.startswith("```"):
                json_str = json_str[3:-3].strip()
                
            judgment = json.loads(json_str)
            logger.info("Meta-Judge synthesis complete", health_score=judgment.get("health_score"))
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Meta-Judge failed to parse JSON", error=str(e), raw_output=raw_response)
            # Minimal fallback judgment
            judgment = {
                "executive_summary": "Analysis complete with some potential issues identified. Manual review recommended.",
                "health_score": 75,
                "top_risks": ["Potential parsing error during synthesis."]
            }

        return {
            "overview": judgment,
            "findings": [f.model_dump() for f in all_findings],
            "agent_summaries": [
                {"agent": r.agent_name, "summary": r.summary}
                for r in reports
            ]
        }
