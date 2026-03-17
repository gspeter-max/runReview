from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
import uuid
from app.services.repo_service import RepoService
from app.providers.groq import GroqProvider
from app.agents.architecture_agent import ArchitectureAgent

app = FastAPI()
repo_service = RepoService()
llm_provider = GroqProvider()
arch_agent = ArchitectureAgent(llm_provider)

class AnalyzeRequest(BaseModel):
    repo_url: str

@app.post("/analyze")
async def analyze_repo(request: AnalyzeRequest):
    job_id = str(uuid.uuid4())
    temp_path = f"/tmp/codeagent/{job_id}"
    
    # Minimal Sync Execution for MVP
    repo_service.clone_repo(request.repo_url, temp_path)
    structure = repo_service.get_file_structure(temp_path)
    analysis = await arch_agent.analyze(structure)
    
    return {
        "job_id": job_id,
        "analysis": analysis
    }
