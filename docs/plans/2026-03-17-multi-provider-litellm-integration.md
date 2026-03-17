# Multi-Provider LiteLLM Integration Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate multiple free LLM providers (Cloudflare, GitHub, Gemini, DeepSeek, Mistral, etc.) using LiteLLM and its Router feature for failover/redundancy.

**Architecture:** Replace the existing `GroqProvider` with a generic `LiteLLMProvider` that uses `litellm.Router`. This will allow the application to failover between different free tiers if one is exhausted (429 errors).

**Tech Stack:**
- Python 3.10+
- LiteLLM
- FastAPI
- Pydantic-Settings (for multi-provider API keys)

---

### Task 1: Update Dependencies and Configuration

**Files:**
- Modify: `pyproject.toml`
- Modify: `app/core/config.py`
- Modify: `.env`

**Step 1: Add LiteLLM to `pyproject.toml`**

Update `dependencies` to include `litellm`.

```toml
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "gitpython",
    "groq",
    "litellm",  # Add this
    "python-dotenv",
    "pydantic-settings",
]
```

**Step 2: Run `pip install`**

Run: `pip install litellm`
Expected: `litellm` installed successfully.

**Step 3: Update `app/core/config.py` to include new API keys**

Add settings for:
- `CLOUDFLARE_API_KEY`
- `CLOUDFLARE_ACCOUNT_ID`
- `GITHUB_API_KEY`
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`
- `MISTRAL_API_KEY`
- `HF_API_KEY`

```python
class Settings(BaseSettings):
    GROQ_API_KEY: str
    CLOUDFLARE_API_KEY: Optional[str] = None
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = None
    GITHUB_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    MISTRAL_API_KEY: Optional[str] = None
    HF_API_KEY: Optional[str] = None
    PROJECT_NAME: str = "CodeAgent"
    
    class Config:
        env_file = ".env"
```

**Step 4: Update `.env` template**

```bash
cat >> .env <<EOF
CLOUDFLARE_API_KEY=
CLOUDFLARE_ACCOUNT_ID=
GITHUB_API_KEY=
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
MISTRAL_API_KEY=
HF_API_KEY=
EOF
```

**Step 5: Commit**

```bash
git add pyproject.toml app/core/config.py .env
git commit -m "chore: add litellm and multi-provider configuration"
```

---

### Task 2: Implement LiteLLM Provider and Router

**Files:**
- Create: `app/providers/litellm_provider.py`
- Modify: `app/providers/__init__.py`

**Step 1: Write `app/providers/litellm_provider.py`**

This provider will initialize a `litellm.Router` with all available models/providers.

```python
from litellm import Router
from app.providers.base import LLMProvider
from app.core.config import settings
import logging

class LiteLLMProvider(LLMProvider):
    def __init__(self):
        model_list = []
        
        if settings.GROQ_API_KEY:
            model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "groq/llama-3.3-70b-versatile",
                    "api_key": settings.GROQ_API_KEY
                }
            })
            
        if settings.GEMINI_API_KEY:
            model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "gemini/gemini-1.5-pro",
                    "api_key": settings.GEMINI_API_KEY
                }
            })
            
        if settings.GITHUB_API_KEY:
             model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "openai/gpt-4o",
                    "api_key": settings.GITHUB_API_KEY,
                    "api_base": "https://models.inference.ai.azure.com"
                }
            })
             
        if settings.DEEPSEEK_API_KEY:
            model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "deepseek/deepseek-chat",
                    "api_key": settings.DEEPSEEK_API_KEY
                }
            })

        self.router = Router(
            model_list=model_list,
            fallbacks=[{"code-analysis": ["code-analysis"]}],
            allowed_fails=1,
            retry_after_429=True
        )

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        response = await self.router.acompletion(
            model="code-analysis",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
```

**Step 2: Write failing test for `LiteLLMProvider`**

Test that it can call at least one provider (use mock for unit tests).

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_providers.py`
Expected: FAIL (or missing file)

**Step 4: Commit**

```bash
git add app/providers/litellm_provider.py
git commit -m "feat: implement LiteLLMProvider with Router for failover"
```

---

### Task 3: Update FastAPI App to use LiteLLMProvider

**Files:**
- Modify: `app/main.py`

**Step 1: Replace `GroqProvider` with `LiteLLMProvider`**

```python
from app.providers.litellm_provider import LiteLLMProvider
# ... other imports

llm_provider = LiteLLMProvider()
# ... rest of the app
```

**Step 2: Test the `/analyze` endpoint**

Run the app and hit the endpoint with a test repo.
Expected: Analysis returned correctly using the router.

**Step 3: Commit**

```bash
git add app/main.py
git commit -m "refactor: use LiteLLMProvider in main application"
```

---

### Task 4: Add Cloudflare and Hugging Face Support

**Files:**
- Modify: `app/providers/litellm_provider.py`

**Step 1: Update `model_list` in `LiteLLMProvider`**

```python
        if settings.CLOUDFLARE_API_KEY and settings.CLOUDFLARE_ACCOUNT_ID:
            model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "cloudflare/@cf/meta/llama-3.1-8b-instruct",
                    "api_key": settings.CLOUDFLARE_API_KEY,
                    "cloudflare_account_id": settings.CLOUDFLARE_ACCOUNT_ID
                }
            })

        if settings.HF_API_KEY:
            model_list.append({
                "model_name": "code-analysis",
                "litellm_params": {
                    "model": "huggingface/meta-llama/Llama-3.1-70B-Instruct",
                    "api_key": settings.HF_API_KEY
                }
            })
```

**Step 2: Commit**

```bash
git add app/providers/litellm_provider.py
git commit -m "feat: add Cloudflare and Hugging Face to LiteLLM Router"
```
