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
from app.rag.pipeline.ingestion_pipeline import IngestionPipeline
from app.rag.config import get_settings
from app.core.logging import logger

app = FastAPI(title="CodeReview API")

# Initialize shared services
repo_service = RepoService()
llm_router = LLMRouter()
rag_settings = get_settings()

# Initialize orchestration components
coordinator = Coordinator(llm_router)
orchestrator = Orchestrator(llm_router)
meta_judge = MetaJudge(llm_router)
ingestion_pipeline = IngestionPipeline(rag_settings, router=llm_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class AnalyzeRequest(BaseModel):
    repo_url: str
    user_request: Optional[str] = "Analyze this repository for security, quality, and architecture."

@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    """
    Main orchestration endpoint:
    Clone -> Ingest (RAG) -> Coordinator (Plan) -> Orchestrator (Execute) -> MetaJudge (Reduce)
    """
    job_id = str(uuid.uuid4())
    temp_path = f"/tmp/codeagent/{job_id}"
    
    logger.info("Starting analysis job", job_id=job_id, repo_url=request.repo_url)
    
    try:
        # Step 1: Clone
        repo_service.clone_repo(request.repo_url, temp_path)
        
        # Step 2: Ingest into RAG
        logger.info("Starting RAG ingestion", job_id=job_id)
        stats = await ingestion_pipeline.run(temp_path)
        logger.info("RAG ingestion complete", job_id=job_id, stats=stats)
        
        # Step 3: Plan with Coordinator
        # Get structure relative to temp_path (now sanitized in RepoService)
        # We implement a depth limit and token budget to avoid Context Window Exhaustion (8k limit)
        structure = repo_service.get_file_structure(temp_path, max_depth=3, max_tokens=3000)
        tasks = await coordinator.plan(structure, request.user_request)
        
        # Step 4: Execute in Parallel with Orchestrator (The "Worker" phase)
        reports = await orchestrator.spawn_agents(tasks, temp_path)
        
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
