import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_dependencies():
    with patch("app.main.repo_service") as mock_repo, \
         patch("app.main.arch_agent") as mock_agent:
        
        mock_repo.get_file_structure.return_value = "mocked structure"
        mock_agent.analyze = AsyncMock(return_value="mocked analysis")
        
        yield mock_repo, mock_agent

def test_analyze_repo_endpoint(mock_dependencies):
    mock_repo, mock_agent = mock_dependencies
    
    response = client.post(
        "/analyze",
        json={"repo_url": "https://github.com/example/repo.git"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["analysis"] == "mocked analysis"
    
    # Verify the services were called correctly
    mock_repo.clone_repo.assert_called_once()
    assert mock_repo.clone_repo.call_args[0][0] == "https://github.com/example/repo.git"
    assert "tmp/codeagent" in mock_repo.clone_repo.call_args[0][1]
    
    mock_repo.get_file_structure.assert_called_once()
    
    mock_agent.analyze.assert_called_once_with("mocked structure")
