import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.coordinator import Coordinator
from app.llmProvider.router import LLMRouter
from app.sdk.agent import AgentTask

@pytest.mark.asyncio
async def test_coordinator_plan_success():
    # Arrange
    mock_provider = MagicMock(spec=LLMRouter)
    mock_provider.generate = AsyncMock(return_value='[{"task_id": "T1", "agent": "security", "instruction": "Check for secrets"}]')
    coordinator = Coordinator(mock_provider)
    
    # Act
    tasks = await coordinator.plan("dummy-structure")
    
    # Assert
    assert len(tasks) == 1
    assert tasks[0].task_id == "T1"
    assert tasks[0].agent == "security"

@pytest.mark.asyncio
async def test_coordinator_plan_json_fallback():
    # Arrange
    mock_provider = MagicMock(spec=LLMRouter)
    mock_provider.generate = AsyncMock(return_value="NOT JSON")
    coordinator = Coordinator(mock_provider)
    
    # Act
    tasks = await coordinator.plan("dummy-structure")
    
    # Assert
    assert len(tasks) == 2
    assert tasks[0].task_id == "fallback-1"
