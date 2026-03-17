import pytest
from app.agents.architecture_agent import ArchitectureAgent
from app.providers.base import LLMProvider
from app.sdk.agent import AgentTask

class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"System: {system_prompt}, Prompt: {prompt}"

@pytest.mark.asyncio
async def test_architecture_agent_analyze():
    provider = MockLLMProvider()
    agent = ArchitectureAgent(provider)
    
    task = AgentTask(task_id="test-1", agent="architecture", instruction="Analyze arch")
    structure = "src/\n    main.py\nREADME.md"
    report = await agent.execute(task, structure)
    
    assert "System: You are an expert software architect." in report.summary
    assert "Prompt: Please analyze the following project structure:" in report.summary
    assert "src/" in report.summary
    assert report.agent_name == "architecture"
