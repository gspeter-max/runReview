# Testing 3 Parallel Agents Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Write comprehensive unit and integration tests that verify the CodeAgent orchestration engine can successfully spawn, manage, and aggregate 3 parallel agents from every angle (success, failure, and aggregation).

**Architecture:** We use `pytest` and `pytest-asyncio`. We will mock the `GroqProvider` so tests run instantly without hitting the actual LLM API.

**Tech Stack:**
- Pytest
- Pytest-Asyncio
- FastAPI TestClient
- Python `unittest.mock`

---

### Task 1: Add the Third "Architecture" Mock Agent

**Files:**
- Modify: `app/agents/mock_agents.py`
- Modify: `app/services/orchestrator.py`

**Step 1: Add `MockArchitectureAgent`**

Add to `app/agents/mock_agents.py`:
```python
class MockArchitectureAgent(BaseAgent):
    """Placeholder architecture agent."""
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        logger.info("Architecture Agent starting", task_id=task.task_id)
        return AgentReport(
            agent_name="architecture",
            findings=[
                Finding(
                    title="Missing Controller Layer",
                    severity="Medium",
                    file_path="main.py",
                    description="All logic is in routes.",
                    suggestion="Separate business logic into services."
                )
            ],
            summary="Architecture is monolithic but functional."
        )
```

**Step 2: Update `AGENT_REGISTRY`**

Update in `app/services/orchestrator.py`:
```python
from app.agents.mock_agents import MockSecurityAgent, MockQualityAgent, MockArchitectureAgent

AGENT_REGISTRY = {
    "security": MockSecurityAgent,
    "quality": MockQualityAgent,
    "architecture": MockArchitectureAgent
}
```

**Step 3: Commit**

```bash
git add app/agents/mock_agents.py app/services/orchestrator.py
git commit -m "test: add mock architecture agent for 3-agent testing"
```

---

### Task 2: Unit Test - Orchestrator (3 Parallel Agents Success)

**Files:**
- Create: `tests/unit/test_orchestrator.py`

**Step 1: Write the passing test**

```python
import pytest
import asyncio
from app.services.orchestrator import Orchestrator
from app.sdk.agent import AgentTask
from app.providers.groq import GroqProvider
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_orchestrator_runs_three_agents_parallel():
    # Arrange
    mock_provider = MagicMock(spec=GroqProvider)
    orchestrator = Orchestrator(mock_provider)
    
    tasks = [
        AgentTask(task_id="1", agent="security", instruction="Test sec"),
        AgentTask(task_id="2", agent="quality", instruction="Test qual"),
        AgentTask(task_id="3", agent="architecture", instruction="Test arch")
    ]
    
    # Act
    reports = await orchestrator.spawn_agents(tasks, "/fake/repo")
    
    # Assert
    assert len(reports) == 3
    agent_names = {r.agent_name for r in reports}
    assert agent_names == {"security", "quality", "architecture"}
    
    # Assert they all succeeded
    for report in reports:
        assert not report.summary.startswith("Error:")
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/unit/test_orchestrator.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/test_orchestrator.py
git commit -m "test: verify orchestrator runs 3 agents in parallel"
```

---

### Task 3: Unit Test - Orchestrator (1 Agent Fails, Others Succeed)

**Files:**
- Modify: `tests/unit/test_orchestrator.py`

**Step 1: Write the failing-agent recovery test**

```python
from app.agents.mock_agents import MockQualityAgent

@pytest.mark.asyncio
async def test_orchestrator_handles_agent_failure(monkeypatch):
    # Arrange
    mock_provider = MagicMock(spec=GroqProvider)
    orchestrator = Orchestrator(mock_provider)
    
    # Force the Quality agent to crash
    async def mock_execute_fail(*args, **kwargs):
        raise ValueError("Quality engine crashed!")
    
    monkeypatch.setattr(MockQualityAgent, "execute", mock_execute_fail)
    
    tasks = [
        AgentTask(task_id="1", agent="security", instruction="Test sec"),
        AgentTask(task_id="2", agent="quality", instruction="Test qual"),
        AgentTask(task_id="3", agent="architecture", instruction="Test arch")
    ]
    
    # Act
    reports = await orchestrator.spawn_agents(tasks, "/fake/repo")
    
    # Assert
    assert len(reports) == 3
    
    quality_report = next(r for r in reports if r.agent_name == "quality")
    assert "Error: Agent execution failed - Quality engine crashed!" in quality_report.summary
    assert len(quality_report.findings) == 0
    
    # Ensure others succeeded
    security_report = next(r for r in reports if r.agent_name == "security")
    assert not security_report.summary.startswith("Error:")
```

**Step 2: Run test**

Run: `pytest tests/unit/test_orchestrator.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/test_orchestrator.py
git commit -m "test: verify orchestrator handles partial agent failures"
```

---

### Task 4: Unit Test - Meta-Judge Aggregation

**Files:**
- Create: `tests/unit/test_meta_judge.py`

**Step 1: Write the test**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.meta_judge import MetaJudge
from app.sdk.agent import AgentReport, Finding
from app.providers.groq import GroqProvider

@pytest.mark.asyncio
async def test_meta_judge_aggregates_three_reports():
    # Arrange
    mock_provider = MagicMock(spec=GroqProvider)
    mock_provider.generate = AsyncMock(return_value="Synthesized 3-agent executive summary.")
    judge = MetaJudge(mock_provider)
    
    reports = [
        AgentReport(agent_name="security", findings=[Finding(title="Bug1", severity="High", file_path="a.py", description="d", suggestion="s")], summary="Sec bad"),
        AgentReport(agent_name="quality", findings=[], summary="Qual good"),
        AgentReport(agent_name="architecture", findings=[Finding(title="Bug2", severity="Medium", file_path="b.py", description="d", suggestion="s")], summary="Arch ok")
    ]
    
    # Act
    final_report = await judge.judge(reports)
    
    # Assert
    assert final_report["overview"]["health_score"] == 70 # 100 - 20 (High) - 10 (Medium)
    assert final_report["overview"]["executive_summary"] == "Synthesized 3-agent executive summary."
    assert len(final_report["findings"]) == 2
    assert len(final_report["agent_summaries"]) == 3
```

**Step 2: Run test**

Run: `pytest tests/unit/test_meta_judge.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/unit/test_meta_judge.py
git commit -m "test: verify meta-judge aggregates 3 reports correctly"
```

---

### Task 5: Integration Test - FastAPI Endpoint

**Files:**
- Create: `tests/integration/test_api.py`

**Step 1: Write the test**

```python
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock
import pytest
import json

client = TestClient(app)

def test_analyze_endpoint_success(monkeypatch):
    # Mock the Coordinator's LLM call to return exactly 3 tasks
    from app.agents.coordinator import Coordinator
    from app.sdk.agent import AgentTask
    
    async def mock_plan(*args, **kwargs):
        return [
            AgentTask(task_id="1", agent="security", instruction="Test"),
            AgentTask(task_id="2", agent="quality", instruction="Test"),
            AgentTask(task_id="3", agent="architecture", instruction="Test")
        ]
    
    monkeypatch.setattr(Coordinator, "plan", mock_plan)
    
    # Mock the MetaJudge's LLM call
    from app.agents.meta_judge import MetaJudge
    async def mock_generate(*args, **kwargs):
        return "Final End-to-End Summary"
    
    # We patch the provider instance inside meta_judge
    monkeypatch.setattr(app.dependency_overrides.get("llm_provider", MetaJudge.__init__), "__init__", lambda self, p: None)
    # The simplest way to mock the provider inside MetaJudge for this test is to patch the provider generate method directly on the instantiated meta_judge
    from app.main import meta_judge
    meta_judge.provider.generate = AsyncMock(return_value="Final End-to-End Summary")
    
    # Act
    response = client.post("/api/v1/analyze", json={"repo_url": "https://github.com/test/test"})
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["status"] == "completed"
    assert len(data["data"]["agent_summaries"]) == 3
    assert data["data"]["overview"]["executive_summary"] == "Final End-to-End Summary"
```

**Step 2: Run test**

Run: `pytest tests/integration/test_api.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/integration/test_api.py
git commit -m "test: full e2e integration test with 3 parallel agents"
```
