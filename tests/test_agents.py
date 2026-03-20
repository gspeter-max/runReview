import pytest
from app.agents.architecture_agent import ArchitectureAgent
from app.providers.base import LLMProvider
from app.sdk.agent import AgentTask

class MockLLMProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"System: {system_prompt}, Prompt: {prompt}"

@pytest.mark.asyncio
async def test_architecture_agent_analyze(tmp_path):
    # Create dummy repo structure
    repo_dir = tmp_path / "dummy_repo"
    repo_dir.mkdir()
    (repo_dir / "src").mkdir()
    (repo_dir / "src" / "main.py").write_text("print('hello')")
    (repo_dir / "README.md").write_text("# Hello")

    provider = MockLLMProvider()
    agent = ArchitectureAgent(provider)
    
    task = AgentTask(task_id="test-1", agent="architecture", instruction="Analyze arch")
    # In the new implementation, 'structure' parameter is actually 'repo_path'
    report = await agent.execute(task, str(repo_dir))
    
    assert "System: You are an expert software architect." in report.summary
    assert "Prompt: Please analyze the following project structure:" in report.summary
    assert "Project Root/" in report.summary
    assert "src/" in report.summary
    assert "main.py" in report.summary
    assert report.agent_name == "architecture"
