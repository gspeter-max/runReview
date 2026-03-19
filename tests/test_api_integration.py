from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import os

# Set environment variable BEFORE importing app
os.environ["GROQ_API_KEY"] = "fake-key"
from app.main import app

client = TestClient(app)

def test_analyze_endpoint_e2e(monkeypatch):
    # Step 1: Mock repo_service.clone_repo to do nothing
    from app.services.repo_service import RepoService
    monkeypatch.setattr(RepoService, "clone_repo", lambda *args: None)
    monkeypatch.setattr(RepoService, "get_file_structure", lambda *args: "mock-structure")
    
    # Step 2: Mock LLM Router for all 3 phases
    from app.llmProvider.router import LLMRouter
    
    async def mock_generate(self, prompt, system_prompt="", **kwargs):
        if "Orchestrator for CodeAgent" in system_prompt:
            # Planner output
            return '[{"task_id": "T1", "agent": "security", "instruction": "Check sec"}]'
        elif "Architecture Agent" in system_prompt or "software architect" in system_prompt:
            # Architecture agent output
            return "Architecture is clean."
        elif "Meta-Judge" or "synthesize" in system_prompt:
            # Meta-Judge output
            return '{"executive_summary": "All good.", "health_score": 90, "top_risks": []}'
        return "Generic Response"

    monkeypatch.setattr(LLMRouter, "generate", mock_generate)

    class MockMessage:
        def __init__(self, content):
            self.content = content
            self.tool_calls = None
        def model_dump(self):
            return {"role": "assistant", "content": self.content}

    async def mock_execute_with_tools(self, messages, tools, model_group):
        system_content = messages[0]["content"] if messages else ""
        if "Architecture Agent" in system_content or "software architect" in system_content:
            return MockMessage("Architecture is clean.")
        return MockMessage('{"findings": []}')
        
    monkeypatch.setattr(LLMRouter, "execute_with_tools", mock_execute_with_tools)

    
    
    
    # Act
    response = client.post("/analyze", json={"repo_url": "https://github.com/test/test"})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "data" in data
    assert data["data"]["overview"]["health_score"] == 90
    assert len(data["data"]["agent_summaries"]) == 1 # Only security task generated
