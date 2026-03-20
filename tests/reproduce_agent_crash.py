import asyncio
import pytest
from unittest.mock import MagicMock, patch

# Mock everything before importing ArchitectureAgent
with patch('app.rag.pipeline.query_pipeline.QueryPipeline'), \
     patch('app.rag.config.Settings'):
    from app.agents.architecture_agent import ArchitectureAgent
    from app.sdk.agent import AgentTask, AgentReport
    from app.llmProvider.router import LLMRouter

class MockLLMProvider:
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"SUMMARY: I see a project at {prompt}"

class MockRouter(LLMRouter):
    def __init__(self):
        self.provider = MockLLMProvider()
    async def generate(self, prompt: str, system_prompt: str = "", model_group: str = "balanced") -> str:
        return await self.provider.generate(prompt, system_prompt)

@pytest.mark.asyncio
async def test_reproduce_box_problem():
    router = MockRouter()
    
    # We still need to mock BaseAgent.__init__ because it's called by ArchitectureAgent
    with patch('app.agents.base.BaseAgent.__init__', return_value=None):
        agent = ArchitectureAgent(router)
        agent.provider = router
        agent.repo_service = MagicMock()
        
        # Simulate what happens in Orchestrator
        task = AgentTask(task_id="job-123", agent="architecture", instruction="Analyze architecture")
        temp_path = "/tmp/codeagent/123e4567-e89b-12d3-a456-426614174000"
        
        report = await agent.execute(task, temp_path)
        
        print(f"\nReport summary: {report.summary}")
        
        # The problem: the prompt contains the raw path, not the structure
        assert temp_path in report.summary
        assert "Repository Root/" not in report.summary # It didn't even get the structure string
