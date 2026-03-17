# Multi-Provider LLM Gateway Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a modular `app/llmProvider/` system that uses LiteLLM Router for failover across multiple free tiers (Groq, Gemini, GitHub, etc.) with YAML configuration and exhaustive testing.

**Architecture:** Adapter Pattern. Each provider has a class in `clients/`. A central `Router` loads these from a `config.yaml` file to manage failover and retries.

**Tech Stack:**
- Python 3.10+
- LiteLLM
- PyYAML
- Pydantic-Settings
- Pytest (with pytest-asyncio and pytest-mock)

---

### Task 1: Scaffolding and Interface

**Files:**
- Create: `app/llmProvider/__init__.py`
- Create: `app/llmProvider/base.py`
- Create: `app/llmProvider/clients/__init__.py`

**Step 1: Implement `app/llmProvider/base.py`**

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseLLMClient(ABC):
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Returns litellm_params for this provider."""
        pass
```

**Step 2: Initialize directories**

Run: `mkdir -p app/llmProvider/clients`
Expected: Directories created.

**Step 3: Commit**

```bash
git add app/llmProvider/
git commit -m "chore: scaffold llmProvider directory and base interface"
```

---

### Task 2: Config Registry and Client Adapters

**Files:**
- Create: `app/llmProvider/config.yaml`
- Create: `app/llmProvider/clients/groq.py`
- Create: `app/llmProvider/clients/gemini.py`
- Create: `app/llmProvider/clients/github.py`

**Step 1: Create `app/llmProvider/config.yaml`**

```yaml
providers:
  - name: groq
    tier: 1 # Fast
    model: groq/llama-3.3-70b-versatile
  - name: gemini
    tier: 2 # Smart
    model: gemini/gemini-1.5-pro
  - name: github
    tier: 2 # Smart
    model: openai/gpt-4o
    api_base: https://models.inference.ai.azure.com
```

**Step 2: Implement `app/llmProvider/clients/groq.py`**

```python
from app.llmProvider.base import BaseLLMClient
from app.core.config import settings

class GroqClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": settings.GROQ_API_KEY
        }
```

**Step 3: Commit**

```bash
git add app/llmProvider/config.yaml app/llmProvider/clients/
git commit -m "feat: add client adapters and YAML config registry"
```

---

### Task 3: LiteLLM Router Implementation

**Files:**
- Create: `app/llmProvider/router.py`

**Step 1: Implement `app/llmProvider/router.py`**

```python
import yaml
from litellm import Router
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient

class LLMRouter:
    def __init__(self, config_path: str = "app/llmProvider/config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        model_list = []
        clients = {
            "groq": GroqClient(),
            "gemini": GeminiClient(),
            "github": GitHubClient()
        }

        for p in config['providers']:
            client = clients.get(p['name'])
            if client:
                params = client.get_config()
                if params.get("api_key"): 
                    model_list.append({
                        "model_name": "code-analyzer",
                        "litellm_params": params
                    })

        self.router = Router(
            model_list=model_list,
            fallbacks=[{"code-analyzer": ["code-analyzer"]}],
            retry_after_429=True
        )

    async def generate(self, prompt: str, system_prompt: str = ""):
        return await self.router.acompletion(
            model="code-analyzer",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
```

**Step 2: Commit**

```bash
git add app/llmProvider/router.py
git commit -m "feat: implement LiteLLM router with tiered loading"
```

---

### Task 4: Comprehensive Test Suite (Testing from All Angles)

**Files:**
- Create: `tests/test_llm_provider.py`

**Step 1: Test Individual Clients (Unit Angle)**
Verify each client returns the correct `litellm_params` and handles missing keys without crashing.

**Step 2: Test Router Failover (Resilience Angle)**
Mock a `429 Rate Limit` from the first provider in the list and verify the router calls the second provider.

```python
@pytest.mark.asyncio
async def test_router_failover(mocker):
    # Mock LiteLLM to fail first, succeed second
    mock_acompletion = mocker.patch("litellm.Router.acompletion")
    mock_acompletion.side_effect = [
        Exception("Rate limit hit"), # First call fails
        MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))]) # Second call succeeds
    ]
    
    router = LLMRouter()
    response = await router.generate("test")
    assert response.choices[0].message.content == "Success"
```

**Step 3: Test Missing Configuration (Edge Case Angle)**
Ensure that if no API keys are provided, the `model_list` is empty and the router gives a clear error or handles it gracefully.

**Step 4: Commit**

```bash
git add tests/test_llm_provider.py
git commit -m "test: add exhaustive test suite for llmProvider and failover"
```

---

### Task 5: Integration and Legacy Cleanup

**Files:**
- Modify: `app/main.py`
- Delete: `app/providers/groq.py`

**Step 1: Update `app/main.py`**
Replace `GroqProvider` with `LLMRouter`.

**Step 2: Run all tests**
Run: `pytest tests/`
Expected: 100% PASS.

**Step 3: Commit**

```bash
git add app/main.py
git rm app/providers/groq.py
git commit -m "refactor: integrate LLMRouter and remove legacy code"
```
