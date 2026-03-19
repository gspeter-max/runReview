import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.orchestrator import Orchestrator
from app.sdk.agent import AgentTask, AgentReport, Finding, Severity
from app.llmProvider.router import LLMRouter

@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    # Arrange
    mock_provider = MagicMock(spec=LLMRouter)
    orchestrator = Orchestrator(mock_provider)
    
    tasks = [
        AgentTask(task_id="1", agent="security", instruction="sec"),
        AgentTask(task_id="2", agent="quality", instruction="qual")
    ]
    
    # Act
    reports = await orchestrator.spawn_agents(tasks, "dummy-path")
    
    # Assert
    assert len(reports) == 2
    agent_names = {r.agent_name for r in reports}
    assert agent_names == {"security", "quality"}

@pytest.mark.asyncio
async def test_orchestrator_handles_agent_crash():
    # Arrange
    mock_provider = MagicMock(spec=LLMRouter)
    orchestrator = Orchestrator(mock_provider)
    
    # Force the quality agent to crash by mocking its execute method
    from app.agents.quality_agent import QualityAgent
    with patch.object(QualityAgent, "execute", side_effect=ValueError("Crashed!")):
        tasks = [
            AgentTask(task_id="1", agent="security", instruction="sec"),
            AgentTask(task_id="2", agent="quality", instruction="qual")
        ]
        
        # Act
        reports = await orchestrator.spawn_agents(tasks, "dummy-path")
        
        # Assert
        assert len(reports) == 2
        quality_report = next(r for r in reports if r.agent_name == "quality")
        assert "Error: Agent execution failed - Crashed!" in quality_report.summary
        assert len(quality_report.findings) == 0
