import pytest
import os
import shutil
from app.services.repo_service import RepoService
from app.llmProvider.router import LLMRouter
from app.agents.coordinator import Coordinator
from app.services.orchestrator import Orchestrator
from app.agents.meta_judge import MetaJudge
from app.sdk.agent import AgentTask

@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires live API keys")
async def test_e2e_authentication_analysis():
    """
    Live E2E test:
    1. Clone real 'authentication' repo
    2. Run full orchestration flow with live LLMs
    3. Verify data consistency
    """
    repo_url = "https://github.com/gspeter-max/authentication.git"
    temp_path = "/tmp/e2e_test_auth"
    
    # Cleanup previous runs
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
        
    try:
        # 1. Setup Services
        repo_service = RepoService()
        llm_router = LLMRouter()
        coordinator = Coordinator(llm_router)
        orchestrator = Orchestrator(llm_router)
        meta_judge = MetaJudge(llm_router)
        
        print(f"\n[E2E] Step 1: Cloning {repo_url}...")
        repo_service.clone_repo(repo_url, temp_path)
        structure = repo_service.get_file_structure(temp_path)
        assert len(structure) > 0
        assert "main.py" in structure or "auth" in structure.lower()
        
        print("[E2E] Step 2: Planning with Coordinator...")
        user_request = "Analyze this authentication repo for security flaws and code quality."
        tasks = await coordinator.plan(structure, user_request)
        
        assert len(tasks) > 0
        for task in tasks:
            assert isinstance(task, AgentTask)
            assert task.model_priority in ["fast", "medium", "reasoning"]
            print(f"  - Planned Task: {task.agent} ({task.model_priority})")
            
        print("[E2E] Step 3: Executing Agents in Parallel...")
        reports = await orchestrator.spawn_agents(tasks, structure)
        assert len(reports) == len(tasks)
        
        print("[E2E] Step 4: Synthesizing with MetaJudge...")
        final_report = await meta_judge.judge(reports)
        
        # 2. Assertions
        assert "overview" in final_report
        assert "health_score" in final_report["overview"]
        assert "executive_summary" in final_report["overview"]
        assert len(final_report["agent_summaries"]) > 0
        
        print(f"\n✅ E2E Test Passed!")
        print(f"Executive Summary: {final_report['overview']['executive_summary'][:150]}...")
        print(f"Final Health Score: {final_report['overview']['health_score']}")

    finally:
        # 3. Cleanup
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)

if __name__ == "__main__":
    # Allow running directly for manual verification
    import asyncio
    asyncio.run(test_e2e_authentication_analysis())
