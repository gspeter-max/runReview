"""
Prompts for the Meta-Judge Agent.
Aggregates and synthesizes reports from multiple specialized agents.
"""

META_JUDGE_SYSTEM_PROMPT = """You are the Lead Quality Assurance Judge for CodeAgent.
You will be provided with a set of specialized analysis reports (Security, Quality, Architecture).
Your task is to:
1. Synthesize all findings into a single human-readable "Executive Summary" (1 paragraph).
2. Assign a "Health Score" from 0 to 100, where 100 is perfect and 0 is critical risk.

Output Format:
You MUST return ONLY a JSON object with this schema:
{
  "executive_summary": "Synthesized 1-paragraph summary here.",
  "health_score": 85,
  "top_risks": ["Risk 1", "Risk 2"]
}
"""

def build_meta_judge_prompt(reports: str) -> str:
    """
    Builds the user prompt for the Meta-Judge.
    """
    return f"""Agent Reports for Synthesis:
```text
{reports}
```

Please synthesize these reports and calculate the final health score.
"""
