# CodeAgent Minimal MVP Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a functional MVP that can clone a GitHub repo, analyze its structure using Groq LLM, and return a JSON report via a FastAPI endpoint.

**Architecture:** Layered architecture with FastAPI for the API, GitPython for repository handling, and an interface-based LLM provider for Groq.

**Tech Stack:** 
- Python 3.10+
- FastAPI
- Groq (LLM)
- GitPython (Cloning)
- Pyproject.toml (Dependency Management)
- Pytest (Testing)

---

### Task 1: Project Initialization & Dependency Management

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `.env`

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "runreview"
version = "0.1.0"
description = "AI-powered codebase analysis platform"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "gitpython",
    "groq",
    "python-dotenv",
    "pydantic-settings",
]

[project.optional-dependencies]
test = [
    "pytest",
    "pytest-asyncio",
    "httpx",
]
```

**Step 2: Initialize project**

Run: `pip install -e ".[test]"`
Expected: Dependencies installed successfully.

**Step 3: Create `.env` template**

```bash
echo "GROQ_API_KEY=your_key_here" > .env
```

**Step 4: Commit**

```bash
git add pyproject.toml .env
git commit -m "chore: initialize project dependencies"
```

---

### Task 2: Core Configuration & LLM Interface

**Files:**
- Create: `app/core/config.py`
- Create: `app/providers/base.py`
- Create: `app/providers/groq.py`

**Step 1: Implement `app/core/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    PROJECT_NAME: str = "CodeAgent"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 2: Implement `app/providers/base.py`**

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        pass
```

**Step 3: Implement `app/providers/groq.py`**

```python
import groq
from app.providers.base import LLMProvider
from app.core.config import settings

class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        completion = await self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        return completion.choices[0].message.content
```

**Step 4: Commit**

```bash
git add app/core/config.py app/providers/
git commit -m "feat: add configuration and groq provider"
```

---

### Task 3: Repository Cloning Service

**Files:**
- Create: `app/services/repo_service.py`

**Step 1: Implement `RepoService`**

```python
import os
import shutil
from git import Repo

class RepoService:
    def clone_repo(self, repo_url: str, target_path: str):
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        Repo.clone_from(repo_url, target_path)

    def get_file_structure(self, path: str) -> str:
        structure = []
        for root, dirs, files in os.walk(path):
            if '.git' in dirs:
                dirs.remove('.git')
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            structure.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f"{sub_indent}{f}")
        return "\n".join(structure)
```

**Step 2: Commit**

```bash
git add app/services/repo_service.py
git commit -m "feat: add repository cloning service"
```

---

### Task 4: Architecture Agent

**Files:**
- Create: `app/agents/architecture_agent.py`

**Step 1: Implement `ArchitectureAgent`**

```python
from app.providers.base import LLMProvider

class ArchitectureAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = "You are an expert software architect. Analyze the provided directory structure and describe the tech stack and architectural pattern."

    async def analyze(self, structure: str) -> str:
        prompt = f"Analyze this project structure:\n\n{structure}"
        return await self.provider.generate(prompt, self.system_prompt)
```

**Step 2: Commit**

```bash
git add app/agents/architecture_agent.py
git commit -m "feat: add architecture agent"
```

---

### Task 5: FastAPI Application & Endpoint

**Files:**
- Create: `app/main.py`

**Step 1: Implement `app/main.py`**

```python
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
```

**Step 2: Commit**

```bash
git add app/main.py
git commit -m "feat: implement fastapi application and analyze endpoint"
```
