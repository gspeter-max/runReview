# Agent Performance Suite Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Optimize LLM agent orchestration and RAG retrieval through parallelism, hierarchical exploration, and smarter context management.

**Architecture:** 
- **Parallelism:** Refactor `BaseAgent` to use `asyncio.gather` for simultaneous tool execution.
- **Hierarchical Exploration:** Add `list_directory` tool to `RepoService` and agent toolkit.
- **Router Alignment:** Map configuration `tier` to `model_group` (fast/medium/reasoning) in `LLMRouter`.
- **Advanced RAG:** Expose `language_filter`, `file_pattern`, and `top_k` in `search_codebase` tool.
- **Smart Truncation:** Support line-range reads in `read_file` and implement head/tail truncation for large files.

**Tech Stack:** Python, asyncio, LiteLLM, LanceDB, tiktoken.

---

### Task 1: Parallel Tool Execution

**Files:**
- Modify: `app/agents/base.py`
- Test: `tests/unit/test_agent_parallelism.py`

**Step 1: Write the failing test**
Create a test that mocks `execute_with_tools` to return multiple tool calls and verifies they are executed concurrently (e.g., by timing or tracking mock calls).

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.agents.base import BaseAgent
from app.sdk.agent import AgentTask

class TestAgent(BaseAgent):
    async def execute(self, task, repo_path):
        return await self.run_agent_loop("sys", task.instruction, repo_path, "medium")

@pytest.mark.asyncio
async def test_parallel_tool_execution():
    provider = MagicMock()
    # Mock message with 2 tool calls
    tool_call1 = MagicMock(id="1")
    tool_call1.function.name = "read_file"
    tool_call1.function.arguments = '{"file_path": "a.py"}'
    
    tool_call2 = MagicMock(id="2")
    tool_call2.function.name = "read_file"
    tool_call2.function.arguments = '{"file_path": "b.py"}'
    
    msg = MagicMock()
    msg.tool_calls = [tool_call1, tool_call2]
    msg.content = None
    msg.model_dump.return_value = {"role": "assistant", "tool_calls": []}
    
    # Second response is the final answer
    final_msg = MagicMock()
    final_msg.tool_calls = []
    final_msg.content = "Done"
    
    provider.execute_with_tools = AsyncMock(side_effect=[msg, final_msg])
    
    agent = TestAgent(provider)
    # Mock global_registry.execute to track timing
    from app.agents.tools import global_registry
    original_execute = global_registry.execute
    
    call_times = []
    async def slow_execute(*args, **kwargs):
        call_times.append(asyncio.get_event_loop().time())
        await asyncio.sleep(0.1)
        return "content"
    
    global_registry.execute = slow_execute
    
    await agent.execute(AgentTask(instruction="test", task_id="1"), "/tmp")
    
    # Restore
    global_registry.execute = original_execute
    
    # If parallel, the difference between start times should be very small
    assert abs(call_times[0] - call_times[1]) < 0.05
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/unit/test_agent_parallelism.py`
Expected: FAIL (currently sequential, so difference will be ~0.1s)

**Step 3: Write implementation**
Modify `app/agents/base.py`:
```python
            # Tool context to pass to tool functions
            tool_context = {
                "repo_path": repo_path,
                "repo_service": self.repo_service,
                "query_pipeline": self.query_pipeline,
                "settings": self.settings
            }
            
            async def process_call(tc):
                content = await global_registry.execute(
                    tool_name=tc.function.name,
                    arguments=tc.function.arguments,
                    context=tool_context
                )
                from app.rag.utils.tokens import truncate_to_tokens
                return {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.function.name,
                    "content": truncate_to_tokens(content, max_tokens=4000)
                }

            tasks = [process_call(tc) for tc in message.tool_calls]
            responses = await asyncio.gather(*tasks)
            messages.extend(responses)
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/unit/test_agent_parallelism.py`
Expected: PASS

**Step 5: Commit**
`git add app/agents/base.py tests/unit/test_agent_parallelism.py && git commit -m "feat(agents): implement parallel tool execution"`

---

### Task 2: Hierarchical Explorer Tool

**Files:**
- Modify: `app/services/repo_service.py`
- Create: `app/agents/tools/explorer.py`
- Modify: `app/agents/tools/__init__.py`
- Test: `tests/unit/test_explorer_tool.py`

**Step 1: Add `list_directory` to `RepoService`**
Modify `app/services/repo_service.py`:
```python
    def list_directory(self, repo_path: str, dir_path: str) -> str:
        full_path = os.path.join(repo_path, dir_path)
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return f"Error: Directory {dir_path} not found."
        
        items = []
        for item in sorted(os.listdir(full_path)):
            if item.startswith('.'): continue
            is_dir = os.path.isdir(os.path.join(full_path, item))
            items.append(f"{'[DIR] ' if is_dir else ''}{item}")
        return "\n".join(items)
```

**Step 2: Create `explorer.py` tool**
Create `app/agents/tools/explorer.py`:
```python
from typing import Any, Dict
import os

def get_list_directory_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the immediate contents of a directory (non-recursive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "The relative path to the directory (use '.' for root)."
                    }
                },
                "required": ["directory_path"]
            }
        }
    }

async def execute_list_directory(context: Dict[str, Any], directory_path: str) -> str:
    repo_service = context.get("repo_service")
    repo_path = context.get("repo_path")
    return repo_service.list_directory(repo_path, directory_path)
```

**Step 3: Register Tool**
Modify `app/agents/tools/__init__.py`:
```python
from app.agents.tools.explorer import get_list_directory_schema, execute_list_directory
global_registry.register("list_directory", get_list_directory_schema(), execute_list_directory)
```

**Step 4: Verify with Test**
Create `tests/unit/test_explorer_tool.py` and verify it lists files correctly.

---

### Task 3: LLM Router & Config Alignment

**Files:**
- Modify: `app/llmProvider/config.yaml`
- Modify: `app/llmProvider/router.py`
- Test: `tests/unit/test_router_alignment.py`

**Step 1: Fix Router logic**
Modify `app/llmProvider/router.py`:
```python
        tier_map = {1: "fast", 2: "medium", 3: "reasoning"}
        for p in config['providers']:
            name = p['name']
            tier = p.get('tier', 2)
            group = tier_map.get(tier, "medium")
            # ... rest same
```

**Step 2: Update Config**
Modify `app/llmProvider/config.yaml`:
- Groq/Cerebras: tier 1
- Gemini/GitHub(GPT-4o): tier 3
- Others: tier 2

---

### Task 4: Advanced RAG Parameters

**Files:**
- Modify: `app/agents/tools/retrieve.py`
- Modify: `app/rag/pipeline/query_pipeline.py`
- Test: `tests/unit/test_rag_params.py`

**Step 1: Update Schema**
Modify `app/agents/tools/retrieve.py` to include `language_filter` and `file_pattern`.

**Step 2: Pass Parameters**
Update `execute_retrieve` and `QueryPipeline.query` to accept and pass these to `CodeRetriever`.

---

### Task 5: Smart Contextual Truncation

**Files:**
- Modify: `app/agents/tools/read.py`
- Modify: `app/services/repo_service.py`
- Modify: `app/rag/utils/tokens.py`
- Test: `tests/unit/test_smart_read.py`

**Step 1: Update `RepoService.read_file`**
Add optional `start_line` and `end_line` parameters.

**Step 2: Implement "Head + Tail" Truncation**
Update `app/rag/utils/tokens.py` to support returning first N and last N tokens if text is too long.

**Step 3: Update `read_file` tool**
Expose `start_line`/`end_line` in schema and use them in execution.
