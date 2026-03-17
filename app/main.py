from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import os
from typing import Optional

from app.services.repo_service import RepoService
from app.llmProvider.router import LLMRouter
from app.agents.coordinator import Coordinator
from app.services.orchestrator import Orchestrator
from app.agents.meta_judge import MetaJudge
from app.core.logging import logger

app = FastAPI(title="CodeReview API")

# Initialize shared services
repo_service = RepoService()
llm_router = LLMRouter()

# Initialize orchestration components
coordinator = Coordinator(llm_router)
orchestrator = Orchestrator(llm_router)
meta_judge = MetaJudge(llm_router)

class AnalyzeRequest(BaseModel):
    repo_url: str
    user_request: Optional[str] = "Analyze this repository for security, quality, and architecture."

@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    """
    Main orchestration endpoint:
    Coordinator (Plan) -> Orchestrator (Execute) -> MetaJudge (Reduce)
    """
    job_id = str(uuid.uuid4())
    temp_path = f"/tmp/codeagent/{job_id}"
    
    logger.info("Starting analysis job", job_id=job_id, repo_url=request.repo_url)
    
    try:
        # Step 1: Clone and gather structure
        repo_service.clone_repo(request.repo_url, temp_path)
        structure = repo_service.get_file_structure(temp_path)
        
        # Step 2: Plan with Coordinator (The "Map" phase)
        tasks = await coordinator.plan(structure, request.user_request)
        
        # Step 3: Execute in Parallel with Orchestrator (The "Worker" phase)
        reports = await orchestrator.spawn_agents(tasks, structure)
        
        # Step 4: Aggregate and Synthesize with MetaJudge (The "Reduce" phase)
        final_rich_report = await meta_judge.judge(reports)
        
        return {
            "job_id": job_id,
            "status": "completed",
            "orchestration_metadata": {
                "coordinator_plan": [t.model_dump() for t in tasks],
                "raw_agent_reports": [r.model_dump() for r in reports]
            },
            "data": final_rich_report
        }

    except Exception as e:
        logger.error("Analysis job failed", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup (Optional: In production, we'd handle this more robustly)
        # In this MVP, we leave it for potential inspection if it's in /tmp
        pass
