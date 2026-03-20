import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

from app.sdk.agent import AgentTask, AgentReport

client = TestClient(app)

@pytest.fixture
def mock_dependencies():
    with patch("app.main.repo_service") as mock_repo, \
         patch("app.main.coordinator") as mock_coord, \
         patch("app.main.orchestrator") as mock_orch, \
         patch("app.main.meta_judge") as mock_judge, \
         patch("app.main.ingestion_pipeline") as mock_ingest:
        
        mock_repo.get_file_structure.return_value = "mocked structure"
        
        # Mock ingestion
        from app.rag.pipeline.ingestion_pipeline import IngestionStats
        mock_ingest.run = AsyncMock(return_value=IngestionStats(0,0,0,0,0,0,[]))
        
        # Mock coordinator plan
        task = AgentTask(task_id="t1", agent="test", instruction="test task")
        mock_coord.plan = AsyncMock(return_value=[task])
        
        # Mock orchestrator spawn_agents
        report = AgentReport(agent_name="test", findings=[], summary="test summary")
        mock_orch.spawn_agents = AsyncMock(return_value=[report])
        
        # Mock meta_judge judge
        mock_judge.judge = AsyncMock(return_value={"final": "report"})
        
        yield mock_repo, mock_coord, mock_orch, mock_judge

def test_analyze_repo_endpoint(mock_dependencies):
    mock_repo, mock_coord, mock_orch, mock_judge = mock_dependencies
    
    response = client.post(
        "/analyze",
        json={"repo_url": "https://github.com/example/repo.git"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "completed"
    assert data["data"] == {"final": "report"}
    
    # Verify the services were called correctly
    mock_repo.clone_repo.assert_called_once()
    mock_coord.plan.assert_called_once()
    mock_orch.spawn_agents.assert_called_once()
    mock_judge.judge.assert_called_once()

