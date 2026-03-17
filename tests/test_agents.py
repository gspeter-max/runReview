import pytest
from app.agents.architecture_agent import ArchitectureAgent
from app.providers.base import LLMProvider

class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"System: {system_prompt}, Prompt: {prompt}"

@pytest.mark.asyncio
async def test_architecture_agent_analyze():
    provider = MockLLMProvider()
    agent = ArchitectureAgent(provider)
    
    structure = "src/\n    main.py\nREADME.md"
    result = await agent.analyze(structure)
    
    assert "System: You are an expert software architect." in result
    assert "Prompt: Please analyze the following project structure:" in result
    assert "src/" in result
